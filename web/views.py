from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Prefetch
from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView

from comercios.selectors import get_comercios_firmados, get_rubros_con_comercios
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
