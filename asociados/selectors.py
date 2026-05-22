from .models import Asociado, InscripcionCurso


def get_asociados_activos():
    return Asociado.objects.filter(estado=Asociado.ESTADO_ACTIVO).select_related("curso_actual", "usuario")


def get_asociado_by_dni(dni: str):
    return Asociado.objects.filter(dni=dni).select_related("curso_actual", "usuario").first()


def get_historial_cursos(asociado_id: int):
    return InscripcionCurso.objects.filter(asociado_id=asociado_id).select_related("curso")

