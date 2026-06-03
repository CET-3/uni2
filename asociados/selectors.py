from django.db.models import Q

from .models import Asociado, InscripcionCurso


def get_asociados_activos():
    return Asociado.objects.filter(estado=Asociado.ESTADO_ACTIVO).select_related("curso_actual", "usuario")


def get_asociado_by_dni(dni: str):
    return Asociado.objects.filter(dni=dni).select_related("curso_actual", "usuario").first()


def get_historial_cursos(asociado_id: int):
    return InscripcionCurso.objects.filter(asociado_id=asociado_id).select_related(
        "curso",
        "ciclo_lectivo",
    )


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


def get_asociado_by_id(asociado_id: int):
    return Asociado.objects.select_related("curso_actual", "usuario").filter(id=asociado_id).first()
