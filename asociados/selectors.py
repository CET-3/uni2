from django.db.models import Q
from django.utils import timezone

from .models import Asociado
from cuotas.selectors import get_total_deuda


def get_asociados_activos():
    return Asociado.objects.filter(estado=Asociado.ESTADO_ACTIVO).select_related("curso_actual", "usuario")


def get_asociado_by_dni(dni: str):
    return Asociado.objects.filter(dni=dni).select_related("curso_actual", "usuario").first()


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
    return Asociado.objects.select_related("curso_actual", "usuario")


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
    usuario: str = "",
    deuda: str = "",
):
    query = (query or "").strip()
    if hasattr(curso_id, "pk"):
        curso_id = curso_id.pk
    curso_id = curso_id or None
    has_filters = any([query, estado, tipo, curso_id, usuario, deuda])
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
    return Asociado.objects.select_related("curso_actual", "usuario").filter(id=asociado_id).first()
