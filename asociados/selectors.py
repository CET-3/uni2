import uuid
import hashlib

from django.db.models import Q
from django.utils import timezone

from .models import Asociado, SolicitudAsociacion
from cuotas.selectors import get_total_deuda


def get_asociados_activos():
    return Asociado.objects.filter(estado=Asociado.ESTADO_ACTIVO).select_related("curso_actual", "clasificacion_adherente", "usuario")


def get_asociado_by_dni(dni: str):
    return Asociado.objects.filter(dni=dni).select_related("curso_actual", "clasificacion_adherente", "usuario").first()


def get_asociado_by_credential_token(token):
    """Busca una credencial sin decidir quién tiene permiso para verla."""

    return Asociado.objects.select_related("curso_actual", "clasificacion_adherente").filter(token_credencial=token).first()


def get_asociado_by_credential_identifier(identifier):
    """Busca por UUID de credencial o por DNI para la validación manual."""

    value = str(identifier or "").strip()
    if not value:
        return None
    try:
        token = uuid.UUID(value)
    except (ValueError, AttributeError):
        return Asociado.objects.filter(dni=value).first()
    return get_asociado_by_credential_token(token)


def search_asociados(query: str):
    query = query.strip()
    if not query:
        return Asociado.objects.none()
    return (
        Asociado.objects.select_related("curso_actual", "usuario")
        .filter(
            Q(dni__icontains=query)
            | Q(numero_asociado__iexact=query)
            | Q(apellido__icontains=query)
            | Q(nombre__icontains=query)
        )
        .order_by("apellido", "nombre")
    )


def _base_queryset():
    return Asociado.objects.select_related("curso_actual", "clasificacion_adherente", "usuario")


def _asociados_con_deuda_ids(fecha_referencia=None):
    if fecha_referencia is None:
        fecha_referencia = timezone.localdate()
    return [
        asociado.id
        for asociado in _base_queryset().order_by("apellido", "nombre")
        if get_total_deuda(asociado, fecha_referencia) > 0
    ]


def filter_asociados(
    *,
    query: str = "",
    estado: str = "",
    tipo: str = "",
    curso_id=None,
    clasificacion_adherente_id=None,
    usuario: str = "",
    deuda: str = "",
):
    query = (query or "").strip()
    if hasattr(curso_id, "pk"):
        curso_id = curso_id.pk
    curso_id = curso_id or None
    has_filters = any([query, estado, tipo, curso_id, clasificacion_adherente_id, usuario, deuda])
    if not has_filters:
        return Asociado.objects.none()

    asociados = _base_queryset()
    if query:
        asociados = asociados.filter(
            Q(dni__icontains=query)
            | Q(numero_asociado__iexact=query)
            | Q(apellido__icontains=query)
            | Q(nombre__icontains=query)
        )
    if estado:
        asociados = asociados.filter(estado=estado)
    if tipo:
        asociados = asociados.filter(tipo=tipo)
    if curso_id:
        asociados = asociados.filter(curso_actual_id=curso_id)
    if clasificacion_adherente_id:
        asociados = asociados.filter(clasificacion_adherente_id=clasificacion_adherente_id)
    if usuario == "con":
        asociados = asociados.filter(usuario__isnull=False)
    elif usuario == "sin":
        asociados = asociados.filter(usuario__isnull=True)
    if deuda:
        ids_con_deuda = _asociados_con_deuda_ids()
        if deuda == "con":
            asociados = asociados.filter(id__in=ids_con_deuda)
        elif deuda == "sin":
            asociados = asociados.exclude(id__in=ids_con_deuda)
    return asociados.order_by("apellido", "nombre")


def get_asociados_for_export(filters=None):
    filters = filters or {}
    return filter_asociados(**filters) if any((filters.get(key) for key in filters)) else _base_queryset().order_by(
        "apellido", "nombre"
    )


def get_asociado_by_id(asociado_id: int):
    return Asociado.objects.select_related("curso_actual", "clasificacion_adherente", "usuario").filter(id=asociado_id).first()


def obtener_solicitud_por_token(token: str, ahora=None):
    if not token:
        return None
    ahora = ahora or timezone.now()
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return (
        SolicitudAsociacion.objects.select_related(
            "curso_actual",
            "clasificacion_adherente",
            "asociado",
        )
        .filter(
            token_seguimiento_hash=token_hash,
            token_seguimiento_vence_en__gt=ahora,
        )
        .first()
    )


def filtrar_solicitudes_asociacion(
    *,
    query="",
    estado="",
    incluir_finales=False,
    tipo="",
    fecha_desde=None,
    fecha_hasta=None,
):
    solicitudes = SolicitudAsociacion.objects.select_related(
        "curso_actual",
        "clasificacion_adherente",
        "asociado",
    )
    query = (query or "").strip()
    if query:
        documento = query.replace(".", "").replace("-", "").replace(" ", "")
        solicitudes = solicitudes.filter(
            Q(nombre__icontains=query)
            | Q(apellido__icontains=query)
            | Q(dni__icontains=query)
            | Q(dni_normalizado__icontains=documento)
            | Q(email__icontains=query)
        )
    if estado:
        solicitudes = solicitudes.filter(estado=estado)
    elif not incluir_finales:
        solicitudes = solicitudes.exclude(
            estado__in=(
                SolicitudAsociacion.ESTADO_ALTA_COMPLETADA,
                SolicitudAsociacion.ESTADO_CANCELADA,
            )
        )
    if tipo:
        solicitudes = solicitudes.filter(tipo=tipo)
    if fecha_desde:
        solicitudes = solicitudes.filter(creado_en__date__gte=fecha_desde)
    if fecha_hasta:
        solicitudes = solicitudes.filter(creado_en__date__lte=fecha_hasta)
    return solicitudes.order_by("creado_en", "id")


def obtener_solicitud_gestion(solicitud_id):
    return (
        SolicitudAsociacion.objects.select_related(
            "curso_actual",
            "clasificacion_adherente",
            "asociado",
            "creado_por",
            "modificado_por",
        )
        .filter(pk=solicitud_id)
        .first()
    )
