from .models import Beneficio, HorarioAtencion


def create_beneficio(**kwargs):
    return Beneficio.objects.create(**kwargs)


def create_horario_atencion(**kwargs):
    return HorarioAtencion.objects.create(**kwargs)
