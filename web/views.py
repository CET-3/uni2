from django.views.generic import TemplateView

from comercios.selectors import get_comercios_firmados
from contenidos.selectors import get_beneficios_publicos


class HomeView(TemplateView):
    template_name = "web/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["beneficios"] = get_beneficios_publicos()[:3]
        context["comercios"] = get_comercios_firmados()[:3]
        return context


class BeneficiosPublicosView(TemplateView):
    template_name = "web/beneficios.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["beneficios"] = get_beneficios_publicos()
        return context


class ComerciosPublicosView(TemplateView):
    template_name = "web/comercios.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comercios"] = get_comercios_firmados()
        return context
