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
    def titulo(self):
        """Describe la operación con vocabulario de negocio cuando es posible."""

        tipos_evento = {(evento.entidad, evento.accion) for evento in self.eventos}
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
