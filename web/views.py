import json
from urllib.parse import urljoin

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Prefetch
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import redirect, render
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.views import View
from django.views.generic import DetailView, FormView, TemplateView

from asociados.models import SolicitudAsociacion
from asociados.selectors import obtener_solicitud_por_token
from asociados.services import (
    CorreccionSolicitudNoPermitida,
    EnlaceSolicitudInvalido,
    LimiteSolicitudExcedido,
    SolicitudAsociacionDuplicada,
    corregir_solicitud_asociacion,
    crear_solicitud_asociacion,
)
from auditoria.selectors import obtener_motivo_ultima_observacion_solicitud

from comercios.selectors import (
    get_comercio_firmado_queryset,
    get_comercios_firmados,
    get_rubros_con_comercios,
)
from comercios.models import ActividadComercial, Comercio
from contenidos.models import CategoriaProductoServicio, ProductoServicio
from contenidos.selectors import (
    get_bloques_productos_publicos,
    get_categorias_productos_servicios_publicas,
    get_publicidades_home,
)
from cuotas.selectors import get_periodo_cuota_para_publicar
from gestion.permissions import GESTION_VER_DESIGN_SYSTEM, user_has_gestion_permission
from usuarios.home_navigation import build_home_navigation

from .forms import PreinscripcionForm, SolicitudAsociacionForm
from .request_utils import obtener_ip_cliente


def robots_txt(request):
    site_origin = settings.UNI2_SITE_URL or request.build_absolute_uri("/").rstrip("/")
    return HttpResponse(
        f"User-agent: *\nSitemap: {site_origin}/sitemap.xml\n",
        content_type="text/plain",
    )


class SolicitudPrivadaResponseMixin:
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        response.headers["X-Robots-Tag"] = "noindex, nofollow"
        return response


class PublicPageSeoMixin:
    seo_description = ""
    seo_suffix = ""
    seo_title = ""
    seo_is_home = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = getattr(self, "object", None)
        path = obj.get_absolute_url() if obj else self.request.path
        site_origin = settings.UNI2_SITE_URL or self.request.build_absolute_uri("/").rstrip("/")
        context["seo_canonical_url"] = f"{site_origin}{path}"
        context["seo_title"] = f"{obj.nombre} | UNI2" if obj else self.seo_title
        context["seo_image_url"] = urljoin(
            f"{site_origin}/", static(f"{settings.PWA_ICON_DIRECTORY}/icon-512.png")
        )
        description = (getattr(obj, "descripcion", "") or "").strip() if obj else self.seo_description
        if obj and "uni2" not in description.casefold():
            description = description or obj.nombre
            separator = " " if description.endswith((".", "!", "?")) else ". "
            description = f"{description}{separator}{self.seo_suffix}"
        context["seo_description"] = description
        structured_data = None
        if self.seo_is_home:
            structured_data = {
                "@context": "https://schema.org",
                "@graph": [
                    {"@type": "WebSite", "name": "UNI2", "url": f"{site_origin}/"},
                    {
                        "@type": "Organization",
                        "name": "Mutual Escolar UNI2",
                        "url": f"{site_origin}/",
                        "logo": context["seo_image_url"],
                        "description": description,
                        "email": "unidosatencionalcliente@gmail.com",
                        "telephone": "+5492984210672",
                        "address": {
                            "@type": "PostalAddress",
                            "streetAddress": "Chacabuco 1050",
                            "addressLocality": "General Roca",
                            "addressRegion": "Río Negro",
                            "addressCountry": "AR",
                        },
                        "sameAs": ["https://www.instagram.com/unidos.cet3"],
                    },
                ],
            }
        elif obj and not (isinstance(obj, Comercio) and obj.estado != Comercio.ESTADO_FIRMADO):
            if isinstance(obj, (CategoriaProductoServicio, ProductoServicio)):
                trail = [("Productos y servicios", f"{site_origin}/#productos-servicios")]
            else:
                trail = [("Comercios", f"{site_origin}/#beneficios")]
            if isinstance(obj, ProductoServicio):
                trail.append((obj.categoria.nombre, f"{site_origin}{obj.categoria.get_absolute_url()}"))
            elif isinstance(obj, Comercio):
                trail.append((obj.actividad_comercial.nombre, f"{site_origin}{obj.actividad_comercial.get_absolute_url()}"))
            trail.append((obj.nombre, context["seo_canonical_url"]))
            structured_data = {
                "@context": "https://schema.org",
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": index, "name": name, "item": url}
                    for index, (name, url) in enumerate(trail, start=1)
                ],
            }
        if structured_data:
            context["seo_structured_data"] = (
                json.dumps(structured_data, ensure_ascii=False)
                .replace("<", "\\u003C")
                .replace(">", "\\u003E")
                .replace("&", "\\u0026")
            )
        return context


class PublicDetailSeoMixin(PublicPageSeoMixin):
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if kwargs.get("slug") != (slugify(self.object.nombre) or "detalle"):
            return HttpResponsePermanentRedirect(self.object.get_absolute_url())
        return self.render_to_response(self.get_context_data(object=self.object))


class PreinscripcionView(SolicitudPrivadaResponseMixin, FormView):
    template_name = "web/preinscripcion.html"
    form_class = PreinscripcionForm
    success_url = reverse_lazy("web:preinscripcion_recibida")

    def form_valid(self, form):
        try:
            crear_solicitud_asociacion(
                datos=form.cleaned_data,
                actor_ip=obtener_ip_cliente(self.request),
            )
        except SolicitudAsociacionDuplicada:
            form.add_error(
                None,
                "No pudimos registrar la preinscripción. Es posible que el "
                "documento ya esté asociado a una persona o a otra solicitud. "
                "Si creés que se trata de un error, contactate con la Mutual.",
            )
            return self.form_invalid(form)
        except LimiteSolicitudExcedido:
            form.add_error(
                None,
                "Realizaste varios intentos. Esperá unos minutos antes de volver "
                "a enviar la preinscripción.",
            )
            return self.form_invalid(form)
        return super().form_valid(form)


class PreinscripcionRecibidaView(SolicitudPrivadaResponseMixin, TemplateView):
    template_name = "web/preinscripcion_recibida.html"


class PreinscripcionCorreccionesRecibidasView(
    SolicitudPrivadaResponseMixin,
    TemplateView,
):
    template_name = "web/preinscripcion_correcciones_recibidas.html"


class SolicitudSeguimientoView(SolicitudPrivadaResponseMixin, View):
    template_name = "web/solicitud_seguimiento.html"
    invalid_template_name = "web/solicitud_enlace_invalido.html"

    def get(self, request, token):
        solicitud = obtener_solicitud_por_token(token)
        if solicitud is None:
            return render(request, self.invalid_template_name)
        return render(
            request,
            self.template_name,
            self._contexto(solicitud),
        )

    def post(self, request, token):
        solicitud = obtener_solicitud_por_token(token)
        if solicitud is None:
            return render(request, self.invalid_template_name)
        if solicitud.estado != SolicitudAsociacion.ESTADO_OBSERVADA:
            return render(request, self.template_name, self._contexto(solicitud))

        form = SolicitudAsociacionForm(request.POST)
        if not form.is_valid():
            return render(
                request,
                self.template_name,
                self._contexto(solicitud, form=form),
            )
        try:
            corregir_solicitud_asociacion(
                solicitud_id=solicitud.pk,
                datos=form.cleaned_data,
                token=token,
                actor_ip=obtener_ip_cliente(request),
            )
        except (EnlaceSolicitudInvalido, CorreccionSolicitudNoPermitida):
            return render(request, self.invalid_template_name)
        except SolicitudAsociacionDuplicada:
            form.add_error(
                None,
                "No pudimos registrar las correcciones. Es posible que el documento "
                "ya esté asociado a una persona o a otra solicitud. Si creés que se "
                "trata de un error, contactate con la Mutual.",
            )
            return render(
                request,
                self.template_name,
                self._contexto(solicitud, form=form),
            )
        except LimiteSolicitudExcedido:
            form.add_error(
                None,
                "Realizaste varios intentos. Esperá unos minutos antes de volver a "
                "enviar las correcciones.",
            )
            return render(
                request,
                self.template_name,
                self._contexto(solicitud, form=form),
            )
        except ValidationError:
            form.add_error(
                None,
                "No pudimos registrar las correcciones. Revisá los datos o intentá "
                "más tarde.",
            )
            return render(
                request,
                self.template_name,
                self._contexto(solicitud, form=form),
            )
        return redirect("web:preinscripcion_correcciones_recibidas")

    def _contexto(self, solicitud, form=None):
        editable = solicitud.estado == SolicitudAsociacion.ESTADO_OBSERVADA
        if editable and form is None:
            form = SolicitudAsociacionForm(
                initial={
                    "nombre": solicitud.nombre,
                    "apellido": solicitud.apellido,
                    "dni": solicitud.dni,
                    "email": solicitud.email,
                    "telefono": solicitud.telefono,
                    "direccion": solicitud.direccion,
                    "es_estudiante_cet3": "si"
                    if solicitud.es_estudiante_cet3
                    else "no",
                    "curso_actual": solicitud.curso_actual,
                    "clasificacion_adherente": solicitud.clasificacion_adherente,
                }
            )
        return {
            "solicitud": solicitud,
            "form": form,
            "explicacion": obtener_motivo_ultima_observacion_solicitud(
                solicitud.pk
            )
            if editable
            else "",
        }


class HomeView(PublicPageSeoMixin, TemplateView):
    template_name = "web/home.html"
    seo_title = "UNI2 | Mutual Escolar"
    seo_is_home = True
    seo_description = "Conocé los servicios y beneficios de UNI2, la mutual escolar del CET 3 de General Roca."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categorias_productos_servicios"] = get_categorias_productos_servicios_publicas()
        context["publicidades"] = get_publicidades_home()
        context["rubros_beneficio"] = get_rubros_con_comercios()
        context["comercios"] = get_comercios_firmados()[:3]
        context["periodo_cuota_publicado"] = get_periodo_cuota_para_publicar()
        context["home_navigation"] = build_home_navigation(
            self.request.user,
            requested_profile=self.request.GET.get("perfil"),
        )
        return context


class ProductosServiciosPublicosView(PublicPageSeoMixin, TemplateView):
    template_name = "web/productos_servicios.html"
    seo_title = "Productos y servicios | UNI2"
    seo_description = "Explorá los productos y servicios de UNI2, la mutual escolar del CET 3 de General Roca."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categorias_productos_servicios"] = get_categorias_productos_servicios_publicas()
        return context


class ComerciosPublicosView(PublicPageSeoMixin, TemplateView):
    template_name = "web/comercios.html"
    seo_title = "Comercios adheridos | UNI2"
    seo_description = "Descubrí los comercios adheridos y sus beneficios para asociados de UNI2, la mutual escolar del CET 3 de General Roca."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comercios"] = get_comercios_firmados()
        return context


class ProductoServicioDetalleView(PublicDetailSeoMixin, DetailView):
    model = ProductoServicio
    template_name = "web/producto_servicio_detalle.html"
    context_object_name = "producto_servicio"
    seo_suffix = "Disponible en la Mutual Escolar UNI2 del CET 3 de General Roca."

    def get_queryset(self):
        return ProductoServicio.objects.filter(activo=True, categoria__activa=True).select_related("categoria")


class ComercioDetalleView(PublicDetailSeoMixin, DetailView):
    model = Comercio
    template_name = "web/comercio_detalle.html"
    context_object_name = "comercio"
    seo_suffix = "Comercio adherido a la Mutual Escolar UNI2 del CET 3 de General Roca."

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if self.object.estado != Comercio.ESTADO_FIRMADO:
            response.headers["X-Robots-Tag"] = "noindex, nofollow"
        return response

    def get_queryset(self):
        return Comercio.objects.select_related("actividad_comercial")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.estado != Comercio.ESTADO_FIRMADO:
            self.template_name = "web/comercio_no_disponible.html"
        return obj


class ComercioDetalleModalView(DetailView):
    model = Comercio
    template_name = "web/_comercio_modal_content.html"
    context_object_name = "comercio"

    def get_queryset(self):
        return get_comercio_firmado_queryset()


class CategoriaProductoServicioDetalleView(PublicDetailSeoMixin, DetailView):
    model = CategoriaProductoServicio
    template_name = "web/categoria_detalle.html"
    context_object_name = "categoria"
    seo_suffix = "Una propuesta de la Mutual Escolar UNI2 del CET 3 de General Roca."

    def get_queryset(self):
        return CategoriaProductoServicio.objects.filter(activa=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bloques_productos"] = get_bloques_productos_publicos(self.object)
        return context


class ActividadComercialDetalleView(PublicDetailSeoMixin, DetailView):
    model = ActividadComercial
    template_name = "web/actividadcomercial_detalle.html"
    context_object_name = "actividad_comercial"
    seo_suffix = "Conocé los comercios adheridos a la Mutual Escolar UNI2 del CET 3 de General Roca."

    def get_queryset(self):
        return ActividadComercial.objects.filter(
            comercios__estado=Comercio.ESTADO_FIRMADO,
        ).distinct().prefetch_related(
            Prefetch(
                "comercios",
                queryset=Comercio.objects.filter(estado=Comercio.ESTADO_FIRMADO).order_by("orden", "nombre"),
            )
        )


class VerDesignSystemRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = reverse_lazy("usuarios:login")
    permission_required = GESTION_VER_DESIGN_SYSTEM

    def test_func(self):
        return user_has_gestion_permission(self.request.user, self.permission_required)


class DesignSystemView(VerDesignSystemRequiredMixin, TemplateView):
    template_name = "web/design-system.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["periodo_cuota_publicado"] = get_periodo_cuota_para_publicar()
        context["proporciones_ejemplo"] = [
            {"titulo": "Credenciales activas", "valor": "25,0 %", "progreso": 25,
             "relacion": "114 de 456 personas de alta", "referencia": "Hoy · datos de ejemplo", "color": "green"},
            {"titulo": "Cumplimiento por monto", "valor": "75,0 %", "progreso": 75,
             "relacion": "$ 750,00 cobrados de $ 1.000,00 generados", "referencia": "Cuotas del período · datos de ejemplo", "color": "blue"},
        ]
        return context


class DesignSystemEstructuraView(VerDesignSystemRequiredMixin, TemplateView):
    template_name = "web/design-system/estructura.html"
