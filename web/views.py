from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Prefetch
from django.shortcuts import redirect
from django.views.generic import DetailView, TemplateView

from comercios.selectors import get_comercios_firmados, get_rubros_con_comercios
from comercios.models import ActividadComercial, Comercio
from contenidos.models import CategoriaProductoServicio, ProductoServicio
from contenidos.selectors import get_categorias_productos_servicios_publicas, get_publicidades_home
from gestion.permissions import GESTION_VER_DESIGN_SYSTEM, user_has_gestion_permission
from usuarios.services import get_available_experiences


class HomeView(TemplateView):
    template_name = "web/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categorias_productos_servicios"] = get_categorias_productos_servicios_publicas()
        context["publicidades"] = get_publicidades_home()
        context["rubros_beneficio"] = get_rubros_con_comercios()
        context["comercios"] = get_comercios_firmados()[:3]
        return context


class SmartStartView(HomeView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            experiences = get_available_experiences(request.user)
            if len(experiences) > 1:
                return redirect("usuarios:selector_panel")
            if experiences == ["gestion"]:
                return redirect("gestion:dashboard")
            if experiences == ["asociado"]:
                return redirect("asociados:dashboard")
            if experiences == ["comercio"]:
                return redirect("comercios:dashboard")
        return super().dispatch(request, *args, **kwargs)


class PublicHomeView(HomeView):
    pass


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
        return CategoriaProductoServicio.objects.filter(activa=True).prefetch_related(
            Prefetch(
                "productos_servicios",
                queryset=ProductoServicio.objects.filter(activo=True).order_by("orden", "nombre"),
            )
        )


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
    login_url = "/usuarios/login/"
    permission_required = GESTION_VER_DESIGN_SYSTEM

    def test_func(self):
        return user_has_gestion_permission(self.request.user, self.permission_required)


class DesignSystemView(VerDesignSystemRequiredMixin, TemplateView):
    template_name = "web/design-system.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["show_site_chrome"] = False
        context["load_theme_script"] = False
        return context
