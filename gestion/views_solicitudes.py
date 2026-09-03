from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.views import View

from asociados.selectors import (
    filtrar_solicitudes_asociacion,
    obtener_solicitud_gestion,
)
from asociados.services import (
    SolicitudAsociacionDuplicada,
    TransicionSolicitudInvalida,
    aprobar_datos_solicitud_asociacion,
    cancelar_solicitud_asociacion,
    completar_alta_solicitud_asociacion,
    observar_solicitud_asociacion,
    reenviar_comunicacion_solicitud,
)
from auditoria.selectors import (
    buscar_operaciones_solicitud,
    obtener_operaciones,
)
from comunicaciones.selectors import listar_entregas_para_origen

from .forms import (
    CancelacionSolicitudForm,
    ConfirmarAltaSolicitudForm,
    FiltroSolicitudesAsociacionForm,
    ObservacionSolicitudForm,
)
from .permissions import (
    GESTION_CANCELAR_SOLICITUDES_ASOCIACION,
    GESTION_COMPLETAR_SOLICITUDES_ASOCIACION,
    GESTION_CONSULTAR_SOLICITUDES_ASOCIACION,
    GESTION_REENVIAR_COMUNICACIONES,
    GESTION_REVISAR_SOLICITUDES_ASOCIACION,
)
from .views import GestionPermissionRequiredMixin


class GestionSolicitudesAsociacionView(
    GestionPermissionRequiredMixin,
    TemplateView,
):
    template_name = "gestion/solicitudes_asociacion.html"
    permission_required = GESTION_CONSULTAR_SOLICITUDES_ASOCIACION

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = FiltroSolicitudesAsociacionForm(self.request.GET or None)
        solicitudes = filtrar_solicitudes_asociacion()
        if form.is_valid():
            estado = form.cleaned_data["estado"]
            solicitudes = filtrar_solicitudes_asociacion(
                query=form.cleaned_data["q"],
                estado=""
                if estado == FiltroSolicitudesAsociacionForm.ESTADO_TODAS
                else estado,
                incluir_finales=(
                    estado == FiltroSolicitudesAsociacionForm.ESTADO_TODAS
                ),
                tipo=form.cleaned_data["tipo"],
                fecha_desde=form.cleaned_data["fecha_desde"],
                fecha_hasta=form.cleaned_data["fecha_hasta"],
            )
        elif form.is_bound:
            solicitudes = solicitudes.none()

        page_obj = Paginator(solicitudes, 25).get_page(self.request.GET.get("page"))
        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        context.update(
            form=form,
            page_obj=page_obj,
            solicitudes=page_obj.object_list,
            querystring=query_params.urlencode(),
        )
        return context


class SolicitudAccionContextMixin:
    accion_titulo = ""
    accion_descripcion = ""
    boton_label = "Confirmar"
    boton_clase = "btn-primary"
    boton_icono = "bi-check-circle"
    es_confirmacion_alta = False

    def obtener_solicitud(self, solicitud_id):
        solicitud = obtener_solicitud_gestion(solicitud_id)
        if solicitud is None:
            raise Http404
        return solicitud

    def render_accion(self, *, solicitud, form):
        return self.render_to_response(
            {
                "solicitud": solicitud,
                "form": form,
                "accion_titulo": self.accion_titulo,
                "accion_descripcion": self.accion_descripcion,
                "boton_label": self.boton_label,
                "boton_clase": self.boton_clase,
                "boton_icono": self.boton_icono,
                "es_confirmacion_alta": self.es_confirmacion_alta,
            }
        )


class GestionSolicitudObservarView(
    SolicitudAccionContextMixin,
    GestionPermissionRequiredMixin,
    TemplateView,
):
    template_name = "gestion/solicitud_asociacion_accion.html"
    permission_required = GESTION_REVISAR_SOLICITUDES_ASOCIACION
    accion_titulo = "Observar solicitud"
    accion_descripcion = "La explicación se enviará por correo y quedará visible en el enlace privado."
    boton_label = "Marcar como observada"
    boton_icono = "bi-eye"

    def get(self, request, solicitud_id):
        return self.render_accion(
            solicitud=self.obtener_solicitud(solicitud_id),
            form=ObservacionSolicitudForm(),
        )

    def post(self, request, solicitud_id):
        solicitud = self.obtener_solicitud(solicitud_id)
        form = ObservacionSolicitudForm(request.POST)
        if not form.is_valid():
            return self.render_accion(solicitud=solicitud, form=form)
        try:
            observar_solicitud_asociacion(
                solicitud_id=solicitud.pk,
                explicacion=form.cleaned_data["explicacion"],
                actor=request.user,
            )
        except (TransicionSolicitudInvalida, ValidationError, ValueError) as error:
            form.add_error(None, str(error) or "La solicitud cambió y no puede observarse.")
            return self.render_accion(solicitud=solicitud, form=form)
        messages.success(request, "La solicitud quedó observada.")
        return redirect("gestion:solicitud_asociacion_detalle", solicitud.pk)


class GestionSolicitudAprobarView(GestionPermissionRequiredMixin, View):
    permission_required = GESTION_REVISAR_SOLICITUDES_ASOCIACION

    def post(self, request, solicitud_id):
        try:
            aprobar_datos_solicitud_asociacion(
                solicitud_id=solicitud_id,
                actor=request.user,
            )
            messages.success(request, "Los datos quedaron aprobados.")
        except (TransicionSolicitudInvalida, ValidationError):
            messages.error(request, "La solicitud cambió o sus datos ya no son válidos.")
        return redirect("gestion:solicitud_asociacion_detalle", solicitud_id)


class GestionSolicitudCancelarView(
    SolicitudAccionContextMixin,
    GestionPermissionRequiredMixin,
    TemplateView,
):
    template_name = "gestion/solicitud_asociacion_accion.html"
    permission_required = GESTION_CANCELAR_SOLICITUDES_ASOCIACION
    accion_titulo = "Cancelar solicitud"
    accion_descripcion = "La cancelación es definitiva para esta solicitud y permite presentar una nueva."
    boton_label = "Cancelar solicitud"
    boton_clase = "btn-danger"
    boton_icono = "bi-x-circle"

    def get(self, request, solicitud_id):
        return self.render_accion(
            solicitud=self.obtener_solicitud(solicitud_id),
            form=CancelacionSolicitudForm(),
        )

    def post(self, request, solicitud_id):
        solicitud = self.obtener_solicitud(solicitud_id)
        form = CancelacionSolicitudForm(request.POST)
        if not form.is_valid():
            return self.render_accion(solicitud=solicitud, form=form)
        try:
            cancelar_solicitud_asociacion(
                solicitud_id=solicitud.pk,
                motivo=form.cleaned_data["motivo"],
                actor=request.user,
            )
        except (TransicionSolicitudInvalida, ValueError) as error:
            form.add_error(None, str(error) or "La solicitud ya no puede cancelarse.")
            return self.render_accion(solicitud=solicitud, form=form)
        messages.success(request, "La solicitud quedó cancelada.")
        return redirect("gestion:solicitud_asociacion_detalle", solicitud.pk)


class GestionSolicitudCompletarView(
    SolicitudAccionContextMixin,
    GestionPermissionRequiredMixin,
    TemplateView,
):
    template_name = "gestion/solicitud_asociacion_accion.html"
    permission_required = GESTION_COMPLETAR_SOLICITUDES_ASOCIACION
    accion_titulo = "Confirmar alta"
    accion_descripcion = "Revisá los datos antes de incorporar a la persona al padrón."
    boton_label = "Confirmar y crear asociado"
    boton_icono = "bi-person-check"
    es_confirmacion_alta = True

    def get(self, request, solicitud_id):
        return self.render_accion(
            solicitud=self.obtener_solicitud(solicitud_id),
            form=ConfirmarAltaSolicitudForm(),
        )

    def post(self, request, solicitud_id):
        solicitud = self.obtener_solicitud(solicitud_id)
        form = ConfirmarAltaSolicitudForm(request.POST)
        if not form.is_valid():
            return self.render_accion(solicitud=solicitud, form=form)
        try:
            resultado = completar_alta_solicitud_asociacion(
                solicitud_id=solicitud.pk,
                actor=request.user,
            )
        except (
            SolicitudAsociacionDuplicada,
            TransicionSolicitudInvalida,
            ValidationError,
            ValueError,
        ) as error:
            form.add_error(None, str(error) or "No se pudo completar el alta.")
            return self.render_accion(solicitud=solicitud, form=form)
        messages.success(request, "El alta quedó completada.")
        return redirect("gestion:asociado_detalle", resultado.asociado.pk)


class GestionSolicitudReenviarView(GestionPermissionRequiredMixin, View):
    permission_required = GESTION_REENVIAR_COMUNICACIONES

    def post(self, request, solicitud_id):
        try:
            reenviar_comunicacion_solicitud(
                solicitud_id=solicitud_id,
                actor=request.user,
            )
            messages.success(request, "La comunicación quedó programada nuevamente.")
        except TransicionSolicitudInvalida:
            messages.error(request, "Este estado no tiene una comunicación para reenviar.")
        return redirect("gestion:solicitud_asociacion_detalle", solicitud_id)


class GestionSolicitudAsociacionDetalleView(
    GestionPermissionRequiredMixin,
    TemplateView,
):
    template_name = "gestion/solicitud_asociacion_detalle.html"
    permission_required = GESTION_CONSULTAR_SOLICITUDES_ASOCIACION

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        solicitud = obtener_solicitud_gestion(kwargs["solicitud_id"])
        if solicitud is None:
            raise Http404
        context.update(
            solicitud=solicitud,
            operaciones=obtener_operaciones(
                buscar_operaciones_solicitud(solicitud.pk)
            ),
            entregas=listar_entregas_para_origen(
                solicitud._meta.label,
                solicitud.pk,
            ),
        )
        return context
