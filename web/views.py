from django.views.generic import TemplateView

from comercios.selectors import get_comercios_firmados
from contenidos.selectors import get_categorias_productos_servicios_publicas


class HomeView(TemplateView):
    template_name = "web/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categorias_productos_servicios"] = get_categorias_productos_servicios_publicas()[:3]
        context["comercios"] = get_comercios_firmados()[:3]
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
