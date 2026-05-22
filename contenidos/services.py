from .models import Beneficio, HorarioAtencion, Publicidad, Servicio


def create_beneficio(**kwargs):
    return Beneficio.objects.create(**kwargs)


def create_servicio(**kwargs):
    return Servicio.objects.create(**kwargs)


def create_publicidad(**kwargs):
    return Publicidad.objects.create(**kwargs)


def create_horario_atencion(**kwargs):
    return HorarioAtencion.objects.create(**kwargs)

