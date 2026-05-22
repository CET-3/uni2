from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView

from cuotas.selectors import get_cuotas_deudoras, get_total_deuda
from usuarios.services import user_is_asociado


class AsociadoRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = "usuarios:login"

    def test_func(self):
        return user_is_asociado(self.request.user) and hasattr(self.request.user, "asociado")

    def handle_no_permission(self):
        if self.request.user.is_authenticated and user_is_asociado(self.request.user):
            messages.warning(
                self.request,
                "Tu usuario tiene rol de asociado, pero todavia no tiene un asociado vinculado.",
            )
            return redirect("contenidos:home")
        return super().handle_no_permission()


class AsociadoDashboardView(AsociadoRequiredMixin, TemplateView):
    template_name = "asociados/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        asociado = self.request.user.asociado
        context["asociado"] = asociado
        context["cuotas_deudoras"] = get_cuotas_deudoras(asociado)[:5]
        context["total_deuda"] = get_total_deuda(asociado)
        return context


class AsociadoCredencialView(AsociadoRequiredMixin, TemplateView):
    template_name = "asociados/credencial.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["asociado"] = self.request.user.asociado
        return context


class AsociadoCuotasView(AsociadoRequiredMixin, TemplateView):
    template_name = "asociados/cuotas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        asociado = self.request.user.asociado
        context["asociado"] = asociado
        context["cuotas"] = asociado.cuotas.select_related("periodo").order_by(
            "-periodo__anio",
            "-periodo__mes",
        )
        context["total_deuda"] = get_total_deuda(asociado)
        return context
