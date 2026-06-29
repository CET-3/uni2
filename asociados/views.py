from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView

from django.utils import timezone

from comercios.selectors import get_rubros_con_comercios
from contenidos.selectors import get_categorias_productos_servicios_publicas, get_publicidades_home
from cuotas.selectors import calcular_estado_cuota, get_total_deuda
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
            return redirect("web:home")
        return super().handle_no_permission()


class AsociadoDashboardView(AsociadoRequiredMixin, TemplateView):
    template_name = "asociados/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["asociado"] = self.request.user.asociado
        context["categorias_productos_servicios"] = get_categorias_productos_servicios_publicas()
        context["rubros_beneficio"] = get_rubros_con_comercios()
        context["publicidades"] = get_publicidades_home()
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
        fecha_referencia = timezone.localdate()
        context["asociado"] = asociado
        cuotas = asociado.cuotas.select_related("periodo", "periodo__ciclo_lectivo").order_by(
            "-periodo__ciclo_lectivo__anio", "-periodo__mes"
        )
        context["fecha_referencia"] = fecha_referencia
        context["cuotas"] = [calcular_estado_cuota(cuota, fecha_referencia) for cuota in cuotas]
        context["total_deuda"] = get_total_deuda(asociado, fecha_referencia)
        return context
