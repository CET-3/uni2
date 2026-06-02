from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView

from asociados.models import Asociado
from asociados.selectors import get_historial_cursos, search_asociados
from cuotas.models import Pago, PeriodoCuota
from cuotas.selectors import get_cuotas_deudoras, get_total_deuda
from cuotas.services import generar_cuotas_para_periodo, registrar_pago

from .forms import AsociadoGestionForm, CobroCuotaForm, PeriodoCuotaForm
from .selectors import get_admin_dashboard_stats, get_asociados_deudores


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return self.request.user.is_staff


class GestionDashboardView(StaffRequiredMixin, TemplateView):
    template_name = "gestion/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_admin_dashboard_stats())
        return context


class GestionDeudoresView(StaffRequiredMixin, TemplateView):
    template_name = "gestion/deudores.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["deudores"] = get_asociados_deudores()
        return context


class GestionAsociadosView(StaffRequiredMixin, TemplateView):
    template_name = "gestion/asociados.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()
        context["query"] = query
        context["asociados"] = search_asociados(query) if query else []
        return context


class GestionAsociadoDetalleView(StaffRequiredMixin, TemplateView):
    template_name = "gestion/asociado_detalle.html"

    def dispatch(self, request, *args, **kwargs):
        self.asociado = get_object_or_404(Asociado, id=kwargs["asociado_id"])
        if request.method == "POST":
            form = AsociadoGestionForm(request.POST, instance=self.asociado)
            if form.is_valid():
                form.save()
                messages.success(request, "Asociado actualizado correctamente.")
                return redirect("gestion:asociado_detalle", asociado_id=self.asociado.id)
            request._asociado_form = form
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        asociado = self.asociado
        fecha_referencia = timezone.localdate()
        cuotas_deudoras = []
        for cuota in get_cuotas_deudoras(asociado):
            cuotas_deudoras.append({"cuota": cuota, "saldo_pendiente": cuota.get_saldo_pendiente(fecha_referencia)})
        context["asociado"] = asociado
        context["fecha_referencia"] = fecha_referencia
        context["total_deuda"] = get_total_deuda(asociado, fecha_referencia)
        context["cuotas_deudoras"] = cuotas_deudoras
        context["historial_cursos"] = get_historial_cursos(asociado.id)[:10]
        context["pagos_recientes"] = Pago.objects.filter(asociado=asociado).order_by("-fecha", "-id")[:10]
        context["admin_change_url"] = reverse("admin:asociados_asociado_change", args=[asociado.id])
        context["cobro_url"] = f"{reverse('gestion:cobros')}?asociado={asociado.id}"
        context["asociado_form"] = getattr(self.request, "_asociado_form", AsociadoGestionForm(instance=asociado))
        return context


class GestionCobrosView(StaffRequiredMixin, TemplateView):
    template_name = "gestion/cobrar_cuotas.html"

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            form = CobroCuotaForm(request.POST)
            if form.is_valid():
                asociado = get_object_or_404(Asociado, id=form.cleaned_data["asociado_id"])
                try:
                    pago = registrar_pago(
                        asociado=asociado,
                        fecha=form.cleaned_data["fecha"],
                        importe=form.cleaned_data["importe"],
                        metodo=form.cleaned_data["metodo"],
                        registrado_por=request.user,
                        observaciones=form.cleaned_data["observaciones"],
                    )
                except ValueError as exc:
                    messages.error(request, str(exc))
                    request._cobro_form = form
                    request._selected_asociado = asociado
                else:
                    messages.success(request, f"Pago #{pago.id} registrado para {asociado.apellido}, {asociado.nombre}.")
                    return redirect(f"{reverse_lazy('gestion:cobros')}?asociado={asociado.id}")
            else:
                asociado_id = form.data.get("asociado_id")
                if asociado_id:
                    request._selected_asociado = Asociado.objects.filter(id=asociado_id).first()
                request._cobro_form = form
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()
        selected_asociado = getattr(self.request, "_selected_asociado", None)
        if selected_asociado is None:
            asociado_id = self.request.GET.get("asociado")
            if asociado_id:
                selected_asociado = Asociado.objects.filter(id=asociado_id).select_related("curso_actual", "usuario").first()

        context["query"] = query
        context["search_results"] = search_asociados(query)[:10] if query else []
        context["selected_asociado"] = selected_asociado
        context["cobro_form"] = getattr(
            self.request,
            "_cobro_form",
            CobroCuotaForm(initial={"asociado_id": selected_asociado.id if selected_asociado else None}),
        )
        if selected_asociado:
            fecha_referencia = timezone.localdate()
            cuotas_deudoras = []
            for cuota in get_cuotas_deudoras(selected_asociado):
                cuotas_deudoras.append(
                    {
                        "cuota": cuota,
                        "total_exigible": cuota.get_total_exigible(fecha_referencia),
                        "saldo_pendiente": cuota.get_saldo_pendiente(fecha_referencia),
                    }
                )
            context["cuotas_deudoras"] = cuotas_deudoras
            context["total_deuda"] = get_total_deuda(selected_asociado, fecha_referencia)
            context["fecha_referencia"] = fecha_referencia
        else:
            context["cuotas_deudoras"] = []
            context["total_deuda"] = 0
            context["fecha_referencia"] = timezone.localdate()
        return context


class GestionPeriodosCuotaView(StaffRequiredMixin, TemplateView):
    template_name = "gestion/periodos_cuota.html"

    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            action = request.POST.get("action")
            if action == "crear_periodo":
                form = PeriodoCuotaForm(request.POST)
                if form.is_valid():
                    periodo = form.save()
                    messages.success(request, f"Periodo {periodo} creado correctamente.")
                    return redirect("gestion:periodos_cuota")
                request._periodo_form = form
            elif action == "generar_cuotas":
                periodo = get_object_or_404(PeriodoCuota, id=request.POST.get("periodo_id"))
                creadas = generar_cuotas_para_periodo(periodo)
                messages.success(request, f"Generacion completada para {periodo}: {creadas} cuotas creadas.")
                return redirect("gestion:periodos_cuota")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["periodos"] = PeriodoCuota.objects.order_by("-anio", "-mes")
        context["periodo_form"] = getattr(self.request, "_periodo_form", PeriodoCuotaForm())
        return context

