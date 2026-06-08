from django.db.models import Q

from .models import Asociado


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


def get_asociados_for_export(query: str = ""):
    query = query.strip()
    if query:
        return search_asociados(query)
    return Asociado.objects.select_related("curso_actual", "usuario").order_by("apellido", "nombre")


def get_asociado_by_id(asociado_id: int):
    return Asociado.objects.select_related("curso_actual", "usuario").filter(id=asociado_id).first()
