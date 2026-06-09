from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView

from asociados.exporters import build_asociados_formato_uni2_xlsx
from asociados.importers import (
    PADRON_IMPORT_SESSION_KEY,
    PadronPreview,
    analyze_padron_xlsx,
    build_revisar_padron_xlsx,
    import_padron_preview,
)
from asociados.models import Asociado
from asociados.selectors import filter_asociados, get_asociados_for_export
from cuotas.importers import (
    CUOTAS_HISTORICAS_SESSION_KEY,
    CuotasHistoricasPreview,
    analyze_cuotas_historicas_xlsx,
    build_revisar_cuotas_historicas_xlsx,
    import_cuotas_historicas_preview,
)
from cuotas.models import Pago, PeriodoCuota
from cuotas.selectors import get_cuotas_deudoras, get_total_deuda
from cuotas.services import generar_cuotas_para_periodo, registrar_pago

from .forms import (
    AsociadoGestionForm,
    CobroCuotaForm,
    ImportarCuotasHistoricasForm,
    ImportarPadronAsociadosForm,
    FiltroAsociadosForm,
    PeriodoCuotaForm,
)
from .permissions import (
    GESTION_ADMINISTRAR_PERIODOS_CUOTA,
    GESTION_COBRAR_CUOTAS,
    GESTION_CONSULTAR_ASOCIADOS,
    GESTION_EDITAR_ASOCIADOS,
    GESTION_EXPORTAR_ASOCIADOS,
    GESTION_IMPORTAR_ASOCIADOS,
    GESTION_IMPORTAR_CUOTAS_HISTORICAS,
    GESTION_VER_DEUDORES,
    user_has_any_gestion_permission,
)
from .selectors import get_asociados_deudores


class GestionPermissionRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    permission_required = None
    raise_exception = True

    def test_func(self):
        if self.permission_required is None:
            return user_has_any_gestion_permission(self.request.user)
        return self.request.user.has_perm(self.permission_required)


class GestionDashboardView(GestionPermissionRequiredMixin, TemplateView):
    template_name = "gestion/dashboard.html"


class GestionDeudoresView(GestionPermissionRequiredMixin, TemplateView):
    template_name = "gestion/deudores.html"
    permission_required = GESTION_VER_DEUDORES

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["deudores"] = get_asociados_deudores()
        return context


class GestionAsociadosView(GestionPermissionRequiredMixin, TemplateView):
    template_name = "gestion/asociados.html"
    permission_required = GESTION_CONSULTAR_ASOCIADOS

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = FiltroAsociadosForm(self.request.GET or None)
        if form.is_valid():
            filters = {
                "query": form.cleaned_data["q"],
                "estado": form.cleaned_data["estado"],
                "tipo": form.cleaned_data["tipo"],
                "curso_id": form.cleaned_data["curso_actual"].id if form.cleaned_data["curso_actual"] else None,
                "usuario": form.cleaned_data["usuario"],
                "deuda": form.cleaned_data["deuda"],
            }
            asociados = filter_asociados(**filters)
        else:
            filters = {}
            asociados = []
        context["form"] = form
        context["query"] = form.data.get("q", "") if form.is_bound else ""
        context["asociados"] = asociados
        return context


class GestionExportarAsociadosView(GestionPermissionRequiredMixin, TemplateView):
    permission_required = GESTION_EXPORTAR_ASOCIADOS

    def get(self, request, *args, **kwargs):
        form = FiltroAsociadosForm(request.GET or None)
        if form.is_valid():
            filters = {
                "query": form.cleaned_data["q"],
                "estado": form.cleaned_data["estado"],
                "tipo": form.cleaned_data["tipo"],
                "curso_id": form.cleaned_data["curso_actual"].id if form.cleaned_data["curso_actual"] else None,
                "usuario": form.cleaned_data["usuario"],
                "deuda": form.cleaned_data["deuda"],
            }
        else:
            filters = {}
        try:
            content = build_asociados_formato_uni2_xlsx(get_asociados_for_export(filters))
        except RuntimeError as exc:
            messages.error(request, str(exc))
            return redirect("gestion:asociados")

        response = HttpResponse(
            content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="asociados_formato_uni2.xlsx"'
        return response


class GestionImportarAsociadosView(GestionPermissionRequiredMixin, TemplateView):
    template_name = "gestion/importar_asociados.html"
    permission_required = GESTION_IMPORTAR_ASOCIADOS

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        if action == "preview":
            form = ImportarPadronAsociadosForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    preview = analyze_padron_xlsx(form.cleaned_data["archivo"])
                except (RuntimeError, ValueError) as exc:
                    messages.error(request, str(exc))
                    request._import_form = form
                else:
                    request.session[PADRON_IMPORT_SESSION_KEY] = preview.as_session_data()
                    request.session.modified = True
                    messages.success(request, "Previsualización generada. Revisá los cursos a crear antes de confirmar.")
                    return redirect("gestion:importar_asociados")
            else:
                request._import_form = form
        elif action == "confirm":
            preview_data = request.session.get(PADRON_IMPORT_SESSION_KEY)
            if not preview_data:
                messages.error(request, "No hay una previsualización pendiente para importar.")
                return redirect("gestion:importar_asociados")

            preview = PadronPreview.from_session_data(preview_data)
            result = import_padron_preview(preview, timezone.localdate())
            request.session.pop(PADRON_IMPORT_SESSION_KEY, None)

            messages.success(
                request,
                (
                    f"Importación completada: {result.creados} creados, "
                    f"{result.actualizados} actualizados, {result.cursos_creados} cursos creados."
                ),
            )
            if result.errores:
                messages.warning(request, f"Se registraron {len(result.errores)} errores durante la importación.")
                request._import_result = result
                return self.render_to_response(self.get_context_data(**kwargs))
            return redirect("gestion:asociados")

        return self.render_to_response(self.get_context_data(**kwargs))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = getattr(self.request, "_import_form", ImportarPadronAsociadosForm())
        context["preview"] = self.request.session.get(PADRON_IMPORT_SESSION_KEY)
        context["result"] = getattr(self.request, "_import_result", None)
        return context


class GestionDescargarAsociadosRevisarView(GestionPermissionRequiredMixin, TemplateView):
    permission_required = GESTION_IMPORTAR_ASOCIADOS

    def get(self, request, *args, **kwargs):
        preview_data = request.session.get(PADRON_IMPORT_SESSION_KEY)
        if not preview_data:
            messages.error(request, "No hay una previsualización pendiente para descargar.")
            return redirect("gestion:importar_asociados")

        preview = PadronPreview.from_session_data(preview_data)
        if not preview.revisar:
            messages.error(request, "No hay filas a revisar para descargar.")
            return redirect("gestion:importar_asociados")

        try:
            content = build_revisar_padron_xlsx(preview)
        except RuntimeError as exc:
            messages.error(request, str(exc))
            return redirect("gestion:importar_asociados")

        response = HttpResponse(
            content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="padron_asociados_a_revisar.xlsx"'
        return response


class GestionImportarCuotasHistoricasView(GestionPermissionRequiredMixin, TemplateView):
    template_name = "gestion/importar_cuotas_historicas.html"
    permission_required = GESTION_IMPORTAR_CUOTAS_HISTORICAS

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        if action == "preview":
            form = ImportarCuotasHistoricasForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    preview = analyze_cuotas_historicas_xlsx(form.cleaned_data["archivo"], timezone.localdate())
                except (RuntimeError, ValueError) as exc:
                    messages.error(request, str(exc))
                    request._import_form = form
                else:
                    request.session[CUOTAS_HISTORICAS_SESSION_KEY] = preview.as_session_data()
                    request.session.modified = True
                    messages.success(request, "Previsualización generada. Revisá las cuotas a importar antes de confirmar.")
                    return redirect("gestion:importar_cuotas_historicas")
            else:
                request._import_form = form
        elif action == "confirm":
            preview_data = request.session.get(CUOTAS_HISTORICAS_SESSION_KEY)
            if not preview_data:
                messages.error(request, "No hay una previsualización pendiente para importar.")
                return redirect("gestion:importar_cuotas_historicas")

            preview = CuotasHistoricasPreview.from_session_data(preview_data)
            result = import_cuotas_historicas_preview(preview, request.user)
            request.session.pop(CUOTAS_HISTORICAS_SESSION_KEY, None)
            messages.success(
                request,
                (
                    f"Importación completada: {result.cuotas_creadas} cuotas creadas, "
                    f"{result.pagos_creados} pagos históricos creados, "
                    f"{result.periodos_creados} períodos creados."
                ),
            )
            if result.errores:
                messages.warning(request, f"Se registraron {len(result.errores)} errores durante la importación.")
                request._import_result = result
                return self.render_to_response(self.get_context_data(**kwargs))
            return redirect("gestion:periodos_cuota")

        return self.render_to_response(self.get_context_data(**kwargs))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = getattr(self.request, "_import_form", ImportarCuotasHistoricasForm())
        context["preview"] = self.request.session.get(CUOTAS_HISTORICAS_SESSION_KEY)
        context["result"] = getattr(self.request, "_import_result", None)
        return context


class GestionDescargarCuotasHistoricasRevisarView(GestionPermissionRequiredMixin, TemplateView):
    permission_required = GESTION_IMPORTAR_CUOTAS_HISTORICAS

    def get(self, request, *args, **kwargs):
        preview_data = request.session.get(CUOTAS_HISTORICAS_SESSION_KEY)
        if not preview_data:
            messages.error(request, "No hay una previsualización pendiente para descargar.")
            return redirect("gestion:importar_cuotas_historicas")

        preview = CuotasHistoricasPreview.from_session_data(preview_data)
        if not preview.revisar:
            messages.error(request, "No hay cuotas a revisar para descargar.")
            return redirect("gestion:importar_cuotas_historicas")

        try:
            content = build_revisar_cuotas_historicas_xlsx(preview)
        except RuntimeError as exc:
            messages.error(request, str(exc))
            return redirect("gestion:importar_cuotas_historicas")

        response = HttpResponse(
            content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="cuotas_historicas_a_revisar.xlsx"'
        return response


class GestionAsociadoDetalleView(GestionPermissionRequiredMixin, TemplateView):
    template_name = "gestion/asociado_detalle.html"
    permission_required = GESTION_CONSULTAR_ASOCIADOS

    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST" and not request.user.has_perm(GESTION_EDITAR_ASOCIADOS):
            raise PermissionDenied
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
        context["pagos_recientes"] = Pago.objects.filter(asociado=asociado).order_by("-fecha", "-id")[:10]
        context["admin_change_url"] = reverse("admin:asociados_asociado_change", args=[asociado.id])
        context["cobro_url"] = f"{reverse('gestion:cobros')}?asociado={asociado.id}"
        context["asociado_form"] = getattr(self.request, "_asociado_form", AsociadoGestionForm(instance=asociado))
        return context


class GestionCobrosView(GestionPermissionRequiredMixin, TemplateView):
    template_name = "gestion/cobrar_cuotas.html"
    permission_required = GESTION_COBRAR_CUOTAS

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
        form = FiltroAsociadosForm(self.request.GET or None)
        if form.is_valid():
            filters = {
                "query": form.cleaned_data["q"],
                "estado": form.cleaned_data["estado"],
                "tipo": form.cleaned_data["tipo"],
                "curso_id": form.cleaned_data["curso_actual"].id if form.cleaned_data["curso_actual"] else None,
                "usuario": form.cleaned_data["usuario"],
                "deuda": form.cleaned_data["deuda"],
            }
            search_results = filter_asociados(**filters)[:10]
        else:
            search_results = []
        selected_asociado = getattr(self.request, "_selected_asociado", None)
        if selected_asociado is None:
            asociado_id = self.request.GET.get("asociado")
            if asociado_id:
                selected_asociado = Asociado.objects.filter(id=asociado_id).select_related("curso_actual", "usuario").first()

        query_params = self.request.GET.copy()
        query_params.pop("asociado", None)
        context["form"] = form
        context["search_results"] = search_results
        context["filtros_querystring"] = query_params.urlencode()
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


class GestionPeriodosCuotaView(GestionPermissionRequiredMixin, TemplateView):
    template_name = "gestion/periodos_cuota.html"
    permission_required = GESTION_ADMINISTRAR_PERIODOS_CUOTA

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
        context["periodos"] = PeriodoCuota.objects.select_related("ciclo_lectivo").order_by("-ciclo_lectivo__anio", "-mes")
        context["periodo_form"] = getattr(self.request, "_periodo_form", PeriodoCuotaForm())
        return context
