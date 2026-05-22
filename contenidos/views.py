from django.views.generic import TemplateView

from comercios.selectors import get_comercios_activos

from .selectors import (
    get_beneficios_publicos,
    get_horarios_activos,
    get_publicidades_vigentes,
    get_servicios_publicos,
)


class HomeView(TemplateView):
    template_name = "public/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["publicidades"] = get_publicidades_vigentes()
        context["beneficios"] = get_beneficios_publicos()[:3]
        context["servicios"] = get_servicios_publicos()[:3]
        context["comercios"] = get_comercios_activos()[:3]
        return context


class BeneficiosPublicosView(TemplateView):
    template_name = "public/beneficios.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["beneficios"] = get_beneficios_publicos()
        return context


class ServiciosPublicosView(TemplateView):
    template_name = "public/servicios.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["servicios"] = get_servicios_publicos()
        return context


class HorariosPublicosView(TemplateView):
    template_name = "public/horarios.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["horarios"] = get_horarios_activos()
        return context


class ComerciosPublicosView(TemplateView):
    template_name = "public/comercios.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comercios"] = get_comercios_activos()
        return context

