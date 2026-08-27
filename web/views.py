from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.db.models import Prefetch
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
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

from .forms import SolicitudAsociacionForm
from .request_utils import obtener_ip_cliente


class SolicitudPrivadaResponseMixin:
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        response.headers["X-Robots-Tag"] = "noindex, nofollow"
        return response


class PreinscripcionView(SolicitudPrivadaResponseMixin, FormView):
    template_name = "web/preinscripcion.html"
    form_class = SolicitudAsociacionForm
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


class HomeView(TemplateView):
    template_name = "web/home.html"

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


class ProductosServiciosPublicosView(TemplateView):
    template_name = "web/productos_servicios.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categorias_productos_servicios"] = get_categorias_productos_servicios_publicas()
        return context


class ComerciosPublicosView(TemplateView):
    template_name = "web/comercios.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comercios"] = get_comercios_firmados()
        return context


class ProductoServicioDetalleView(DetailView):
    model = ProductoServicio
    template_name = "web/producto_servicio_detalle.html"
    context_object_name = "producto_servicio"

    def get_queryset(self):
        return ProductoServicio.objects.filter(activo=True, categoria__activa=True).select_related("categoria")


class ComercioDetalleView(DetailView):
    model = Comercio
    template_name = "web/comercio_detalle.html"
    context_object_name = "comercio"

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


class CategoriaProductoServicioDetalleView(DetailView):
    model = CategoriaProductoServicio
    template_name = "web/categoria_detalle.html"
    context_object_name = "categoria"

    def get_queryset(self):
        return CategoriaProductoServicio.objects.filter(activa=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bloques_productos"] = get_bloques_productos_publicos(self.object)
        return context


class ActividadComercialDetalleView(DetailView):
    model = ActividadComercial
    template_name = "web/actividadcomercial_detalle.html"
    context_object_name = "actividad_comercial"

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
        return context


class DesignSystemEstructuraView(VerDesignSystemRequiredMixin, TemplateView):
    template_name = "web/design-system/estructura.html"
