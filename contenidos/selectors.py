from django.db.models import Q

from .models import Beneficio, HorarioAtencion


def get_beneficios_publicos():
    return Beneficio.objects.filter(activo=True)


def get_horarios_activos():
    return HorarioAtencion.objects.filter(activo=True)
