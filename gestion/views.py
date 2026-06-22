from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
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
from cuotas.selectors import (
    calcular_estado_cuota,
    describir_pago,
    get_cuotas_deudoras,
    get_cuotas_del_anio,
    get_cuotas_del_asociado,
    get_total_deuda,
)
from cuotas.services import generar_cuotas_iniciales_para_asociado, generar_cuotas_para_periodo, registrar_pago

from .forms import (
    AsociadoAltaForm,
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
from usuarios.services import create_user_for_asociado


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
        query_params = self.request.GET.copy()
        search_submitted = bool(query_params)

        form = FiltroAsociadosForm(query_params if search_submitted else None)
        if search_submitted and form.is_valid():
            filters = {
                "query": form.cleaned_data["q"],
                "estado": form.cleaned_data["estado"],
                "tipo": form.cleaned_data["tipo"],
                "curso_id": form.cleaned_data["curso_actual"].id if form.cleaned_data["curso_actual"] else None,
                "usuario": form.cleaned_data["usuario"],
                "deuda": form.cleaned_data["deuda"],
            }
            asociados = get_asociados_for_export(filters)
        else:
            filters = {}
            asociados = []
        context["form"] = form
        context["query"] = form.data.get("q", "") if form.is_bound else ""
        context["asociados"] = asociados
        return context


class GestionAsociadoNuevoView(GestionPermissionRequiredMixin, TemplateView):
    template_name = "gestion/asociado_form.html"
    permission_required = GESTION_EDITAR_ASOCIADOS

    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            form = AsociadoAltaForm(request.POST)
            if form.is_valid():
                asociado = form.save()
                cuotas_generadas = generar_cuotas_iniciales_para_asociado(
                    asociado=asociado,
                    fecha_referencia=asociado.fecha_alta,
                )
                if cuotas_generadas:
                    messages.success(
                        request,
                        f"Asociado creado correctamente. Se generaron {len(cuotas_generadas)} cuotas iniciales.",
                    )
                else:
                    messages.success(request, "Asociado creado correctamente. No se generaron cuotas iniciales.")
                if request.user.has_perm(GESTION_COBRAR_CUOTAS):
                    return redirect(f"{reverse('gestion:cobros')}?asociado={asociado.id}")
                return redirect("gestion:asociado_detalle", asociado_id=asociado.id)
            request._asociado_form = form
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = getattr(self.request, "_asociado_form", AsociadoAltaForm())
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
        self.asociado = get_object_or_404(Asociado, id=kwargs["asociado_id"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        asociado = self.asociado
        fecha_referencia = timezone.localdate()
        anio_actual = fecha_referencia.year
        cuotas_anio_actual = []
        for cuota in get_cuotas_del_anio(asociado, anio_actual).order_by("periodo__mes", "id"):
            cuotas_anio_actual.append(calcular_estado_cuota(cuota, fecha_referencia))
        context["asociado"] = asociado
        context["fecha_referencia"] = fecha_referencia
        context["total_deuda"] = get_total_deuda(asociado, fecha_referencia)
        context["cuotas_anio_actual"] = cuotas_anio_actual
        pagos_recientes = Pago.objects.filter(asociado=asociado).order_by("-fecha", "-id")[:10]
        context["pagos_recientes"] = [describir_pago(pago) for pago in pagos_recientes]
        context["cobro_url"] = f"{reverse('gestion:cobros')}?asociado={asociado.id}"
        context["cuotas_url"] = reverse("gestion:asociado_cuotas", args=[asociado.id])
        return context


class GestionAsociadoCuotasView(GestionPermissionRequiredMixin, TemplateView):
    template_name = "gestion/asociado_cuotas.html"
    permission_required = GESTION_CONSULTAR_ASOCIADOS

    def dispatch(self, request, *args, **kwargs):
        self.asociado = get_object_or_404(Asociado, id=kwargs["asociado_id"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        asociado = self.asociado
        fecha_referencia = timezone.localdate()
        context["asociado"] = asociado
        context["fecha_referencia"] = fecha_referencia
        context["total_deuda"] = get_total_deuda(asociado, fecha_referencia)
        cuotas = get_cuotas_del_asociado(asociado).order_by("-periodo__ciclo_lectivo__anio", "-periodo__mes", "-id")
        context["cuotas"] = [calcular_estado_cuota(cuota, fecha_referencia) for cuota in cuotas]
        return context


class GestionAsociadoEditarView(GestionPermissionRequiredMixin, TemplateView):
    template_name = "gestion/asociado_editar.html"
    permission_required = GESTION_EDITAR_ASOCIADOS

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
        context["asociado"] = self.asociado
        context["form"] = getattr(self.request, "_asociado_form", AsociadoGestionForm(instance=self.asociado))
        return context


class GestionCrearUsuarioAsociadoView(GestionPermissionRequiredMixin, TemplateView):
    permission_required = GESTION_EDITAR_ASOCIADOS

    def post(self, request, *args, **kwargs):
        asociado = get_object_or_404(Asociado, id=kwargs["asociado_id"])
        try:
            user = create_user_for_asociado(
                asociado=asociado,
                password=request.POST.get("password", str(asociado.dni)),
            )
            messages.success(request, f"Usuario «{user.username}» creado y vinculado a {asociado.apellido}, {asociado.nombre}.")
        except ValueError as exc:
            messages.error(request, str(exc))
        return redirect("gestion:asociado_detalle", asociado_id=asociado.id)

    def get(self, request, *args, **kwargs):
        return redirect("gestion:asociado_detalle", asociado_id=kwargs["asociado_id"])


class GestionCobrosView(GestionPermissionRequiredMixin, TemplateView):
    template_name = "gestion/cobrar_cuotas.html"
    permission_required = GESTION_COBRAR_CUOTAS

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            asociado = None
            asociado_id = request.POST.get("asociado_id")
            if asociado_id:
                asociado = Asociado.objects.filter(id=asociado_id).first()
            cuotas_queryset = get_cuotas_deudoras(asociado) if asociado else []
            form = CobroCuotaForm(request.POST, cuotas_queryset=cuotas_queryset)
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
                        cuotas_ids=form.cleaned_data["cuotas_ids"],
                    )
                except ValueError as exc:
                    messages.error(request, str(exc))
                    request._cobro_form = form
                    request._selected_asociado = asociado
                else:
                    messages.success(request, f"Pago #{pago.id} registrado para {asociado.apellido}, {asociado.nombre}.")
                    return redirect(f"{reverse_lazy('gestion:cobros')}?asociado={asociado.id}")
            else:
                request._selected_asociado = asociado
                request._cobro_form = form
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_asociado = getattr(self.request, "_selected_asociado", None)
        if selected_asociado is None:
            asociado_id = self.request.GET.get("asociado")
            if asociado_id:
                selected_asociado = Asociado.objects.filter(id=asociado_id).select_related("curso_actual", "usuario").first()

        context["selected_asociado"] = selected_asociado
        if selected_asociado:
            fecha_referencia = timezone.localdate()
            cuotas_deudoras = []
            for cuota in get_cuotas_deudoras(selected_asociado):
                cuotas_deudoras.append(calcular_estado_cuota(cuota, fecha_referencia))
            context["cuotas_deudoras"] = cuotas_deudoras
            context["total_deuda"] = get_total_deuda(selected_asociado, fecha_referencia)
            context["fecha_referencia"] = fecha_referencia
        else:
            context["cuotas_deudoras"] = []
            context["total_deuda"] = 0
            context["fecha_referencia"] = timezone.localdate()
        context["cobro_form"] = getattr(
            self.request,
            "_cobro_form",
            CobroCuotaForm(
                initial={"asociado_id": selected_asociado.id if selected_asociado else None},
                cuotas_queryset=[item.cuota for item in context["cuotas_deudoras"]],
            ),
        )
        context["selected_cuotas_ids"] = set(context["cobro_form"].data.getlist("cuotas_ids"))
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
