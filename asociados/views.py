from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView

from django.utils import timezone

from cuotas.selectors import calcular_estado_credencial, calcular_estado_cuota, get_total_deuda
from usuarios.mixins import AsociadoRequiredMixin, CredentialPrivacyHeadersMixin

from .forms import AsociadoDatosPropiosForm
from .services import actualizar_datos_propios_asociado


class AsociadoCredencialView(CredentialPrivacyHeadersMixin, AsociadoRequiredMixin, TemplateView):
    template_name = "asociados/credencial.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        asociado = self.request.user.asociado
        context["asociado"] = asociado
        dato_etiqueta, dato_valor = asociado.get_dato_institucional()
        context["dato_institucional_etiqueta"] = dato_etiqueta
        context["dato_institucional_valor"] = dato_valor
        context["estado_credencial"] = calcular_estado_credencial(asociado, timezone.localdate())
        context["credencial_url"] = self.request.build_absolute_uri(
            reverse(
                "usuarios:resolver_credencial",
                kwargs={"token": asociado.token_credencial},
            )
        )
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
        cuotas_calculadas = [calcular_estado_cuota(cuota, fecha_referencia) for cuota in cuotas]
        context["cuotas"] = cuotas_calculadas
        context["total_deuda"] = get_total_deuda(asociado, fecha_referencia)
        context["cuotas_total"] = len(cuotas_calculadas)
        context["cuotas_con_saldo"] = sum(1 for cuota in cuotas_calculadas if cuota.saldo > 0)
        return context


class AsociadoDatosPropiosView(AsociadoRequiredMixin, FormView):
    template_name = "asociados/datos_propios.html"
    form_class = AsociadoDatosPropiosForm
    success_url = reverse_lazy("asociados:datos_propios")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.request.user.asociado
        return kwargs

    def form_valid(self, form):
        actualizar_datos_propios_asociado(
            asociado=self.request.user.asociado,
            datos=form.cleaned_data,
            actor=self.request.user,
        )
        messages.success(
            self.request,
            "Tus datos se actualizaron correctamente.",
        )
        return super().form_valid(form)
