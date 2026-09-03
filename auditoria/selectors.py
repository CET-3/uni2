from dataclasses import dataclass
from uuid import UUID

from django.db.models import Max, Q

from .models import EventoAuditoria


@dataclass(frozen=True)
class OperacionAuditoria:
    """Una operación y todos los eventos inmutables que la componen."""

    operacion_id: UUID
    eventos: tuple[EventoAuditoria, ...]

    @property
    def es_compuesta(self):
        return len(self.eventos) > 1

    @property
    def fecha(self):
        return self.eventos[0].fecha

    @property
    def actor_etiqueta(self):
        return self.eventos[0].actor_etiqueta

    @property
    def icono(self):
        tipos_evento = {(evento.entidad, evento.accion) for evento in self.eventos}
        if ("cuotas.Pago", EventoAuditoria.ACCION_CREAR) in tipos_evento:
            return "bi-cash-coin"
        if ("cuotas.Donacion", EventoAuditoria.ACCION_CREAR) in tipos_evento:
            return "bi-heart"
        if ("asociados.Asociado", EventoAuditoria.ACCION_CREAR) in tipos_evento:
            return "bi-person-plus"
        if ("auth.User", EventoAuditoria.ACCION_CREAR) in tipos_evento:
            return "bi-person-lock"
        if all(evento.entidad == "cuotas.Cuota" for evento in self.eventos):
            return "bi-receipt"
        eventos_solicitud = [
            evento
            for evento in self.eventos
            if evento.entidad == "asociados.SolicitudAsociacion"
        ]
        if eventos_solicitud:
            evento = eventos_solicitud[0]
            if evento.accion == EventoAuditoria.ACCION_CREAR:
                return "bi-clipboard-plus"
            estado_nuevo = evento.cambios.get("estado", {}).get("nuevo")
            if estado_nuevo in {"observada", "cancelada"}:
                return "bi-clipboard-x"
            if estado_nuevo == "datos_aprobados":
                return "bi-clipboard-check"
            return "bi-clipboard"
        return "bi-arrow-repeat"

    @property
    def motivo(self):
        return next((evento.motivo for evento in self.eventos if evento.motivo), "")

    @property
    def titulo(self):
        """Describe la operación con vocabulario de negocio cuando es posible."""

        tipos_evento = {(evento.entidad, evento.accion) for evento in self.eventos}
        if (
            ("cuotas.Pago", EventoAuditoria.ACCION_CREAR) in tipos_evento
            and ("cuotas.Donacion", EventoAuditoria.ACCION_CREAR) in tipos_evento
            and not any(evento.entidad == "cuotas.PagoCuota" for evento in self.eventos)
        ):
            return "Registro de donación"
        if ("cuotas.Pago", EventoAuditoria.ACCION_CREAR) in tipos_evento:
            return "Cobro de cuotas"
        if ("asociados.Asociado", EventoAuditoria.ACCION_CREAR) in tipos_evento:
            return "Alta de asociado"
        if (
            ("auth.User", EventoAuditoria.ACCION_CREAR) in tipos_evento
            and any(evento.accion == EventoAuditoria.ACCION_VINCULAR for evento in self.eventos)
        ):
            return "Creación y vinculación de usuario"
        if all(
            evento.entidad == "cuotas.Cuota" and evento.accion == EventoAuditoria.ACCION_CREAR
            for evento in self.eventos
        ):
            return "Generación de cuotas"
        for evento in self.eventos:
            if evento.entidad != "asociados.SolicitudAsociacion":
                continue
            estado_nuevo = evento.cambios.get("estado", {}).get("nuevo")
            titulos_por_estado = {
                "observada": "Solicitud observada",
                "datos_aprobados": "Datos aprobados",
                "cancelada": "Solicitud cancelada",
            }
            if estado_nuevo in titulos_por_estado:
                return titulos_por_estado[estado_nuevo]
            if estado_nuevo == "recibida" and evento.accion == EventoAuditoria.ACCION_MODIFICAR:
                return "Correcciones recibidas"
            if evento.accion == EventoAuditoria.ACCION_CREAR:
                return "Solicitud recibida"
        return "Cambios relacionados"


def buscar_eventos(
    *,
    actor_query="",
    objeto_query="",
    accion="",
    entidad="",
    objeto_id="",
    origen="",
    fecha_desde=None,
    fecha_hasta=None,
):
    eventos = EventoAuditoria.objects.select_related("actor")
    if actor_query:
        eventos = eventos.filter(
            Q(actor_etiqueta__icontains=actor_query)
            | Q(actor__username__icontains=actor_query)
            | Q(actor__first_name__icontains=actor_query)
            | Q(actor__last_name__icontains=actor_query)
        )
    if objeto_query:
        eventos = eventos.filter(
            Q(objeto_descripcion__icontains=objeto_query)
            | Q(objeto_id__icontains=objeto_query)
        )
    if accion:
        eventos = eventos.filter(accion=accion)
    if entidad:
        eventos = eventos.filter(entidad=entidad)
    if objeto_id:
        eventos = eventos.filter(objeto_id=objeto_id)
    if origen:
        eventos = eventos.filter(origen=origen)
    if fecha_desde:
        eventos = eventos.filter(fecha__date__gte=fecha_desde)
    if fecha_hasta:
        eventos = eventos.filter(fecha__date__lte=fecha_hasta)
    return eventos


def listar_entidades_auditadas():
    """Devuelve las entidades que tienen eventos, sin nombres hardcodeados."""

    return list(
        EventoAuditoria.objects.order_by("entidad")
        .values_list("entidad", flat=True)
        .distinct()
    )


def obtener_motivo_ultima_observacion_solicitud(solicitud_id):
    evento = (
        EventoAuditoria.objects.filter(
            entidad="asociados.SolicitudAsociacion",
            objeto_id=str(solicitud_id),
            cambios__estado__nuevo="observada",
        )
        .exclude(motivo="")
        .order_by("-fecha", "-id")
        .first()
    )
    return evento.motivo if evento else ""


def buscar_operaciones(**filtros):
    """Busca operaciones que tengan al menos un evento coincidente.

    La consulta devuelve una fila por ``operacion_id`` para que la paginación
    no divida una misma operación entre páginas.
    """

    return (
        buscar_eventos(**filtros)
        .order_by()
        .values("operacion_id")
        .annotate(
            ultima_fecha=Max("fecha"),
            ultimo_evento_id=Max("id"),
        )
        .order_by("-ultima_fecha", "-ultimo_evento_id")
    )


def buscar_operaciones_asociado(asociado_id):
    """Busca operaciones vinculadas de forma estructurada con un asociado.

    Además de los cambios sobre ``Asociado``, incluye eventos de entidades que
    guardan la relación en ``cambios.asociado`` (por ejemplo cuotas, pagos y
    donaciones). No se usa la descripción visible como criterio de búsqueda.
    """

    asociado_id = int(asociado_id)
    eventos = EventoAuditoria.objects.filter(
        Q(entidad="asociados.Asociado", objeto_id=str(asociado_id))
        | Q(cambios__asociado__anterior__id=asociado_id)
        | Q(cambios__asociado__nuevo__id=asociado_id)
    )
    return (
        eventos.order_by()
        .values("operacion_id")
        .annotate(
            ultima_fecha=Max("fecha"),
            ultimo_evento_id=Max("id"),
        )
        .order_by("-ultima_fecha", "-ultimo_evento_id")
    )


def buscar_operaciones_solicitud(solicitud_id):
    return buscar_operaciones(
        entidad="asociados.SolicitudAsociacion",
        objeto_id=str(solicitud_id),
    )


def obtener_operaciones(resumenes):
    """Carga completos los eventos de las operaciones de una página.

    Aunque un filtro coincida con un solo evento, se recuperan sus eventos
    relacionados para no presentar una operación recortada.
    """

    ids_ordenados = [resumen["operacion_id"] for resumen in resumenes]
    if not ids_ordenados:
        return []

    eventos_por_operacion = {operacion_id: [] for operacion_id in ids_ordenados}
    eventos = (
        EventoAuditoria.objects.select_related("actor")
        .filter(operacion_id__in=ids_ordenados)
        .order_by("operacion_id", "-fecha", "-id")
    )
    for evento in eventos:
        eventos_por_operacion[evento.operacion_id].append(evento)

    return [
        OperacionAuditoria(
            operacion_id=operacion_id,
            eventos=tuple(eventos_por_operacion[operacion_id]),
        )
        for operacion_id in ids_ordenados
    ]


def obtener_operaciones_asociado(resumenes, asociado_id):
    """Carga operaciones del asociado sin filtrar de más ni exponer terceros.

    Una operación ordinaria pertenece a un solo asociado y se muestra completa
    para conservar juntos, por ejemplo, el pago, sus imputaciones y la cuota
    actualizada. Si una operación masiva contiene eventos de varios asociados,
    se conservan únicamente los eventos que refieren al asociado consultado.
    """

    asociado_id = int(asociado_id)
    operaciones = obtener_operaciones(resumenes)
    resultado = []
    for operacion in operaciones:
        ids_relacionados = {
            relacionado_id
            for evento in operacion.eventos
            for relacionado_id in _ids_asociados_del_evento(evento)
        }
        if len(ids_relacionados) <= 1:
            resultado.append(operacion)
            continue

        eventos_del_asociado = tuple(
            evento
            for evento in operacion.eventos
            if asociado_id in _ids_asociados_del_evento(evento)
        )
        if eventos_del_asociado:
            resultado.append(
                OperacionAuditoria(
                    operacion_id=operacion.operacion_id,
                    eventos=eventos_del_asociado,
                )
            )
    return resultado


def _ids_asociados_del_evento(evento):
    ids = set()
    if evento.entidad == "asociados.Asociado":
        try:
            ids.add(int(evento.objeto_id))
        except (TypeError, ValueError):
            pass

    cambio_asociado = evento.cambios.get("asociado", {})
    if not isinstance(cambio_asociado, dict):
        return ids
    for momento in ("anterior", "nuevo"):
        referencia = cambio_asociado.get(momento)
        if not isinstance(referencia, dict) or "id" not in referencia:
            continue
        try:
            ids.add(int(referencia["id"]))
        except (TypeError, ValueError):
            continue
    return ids
