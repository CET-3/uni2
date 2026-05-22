from django.db.models import Q
from django.utils import timezone

from .models import Beneficio, HorarioAtencion, Publicidad, Servicio


def get_beneficios_publicos():
    return Beneficio.objects.filter(activo=True)


def get_servicios_publicos():
    return Servicio.objects.filter(activo=True)


def get_publicidades_vigentes():
    today = timezone.localdate()
    return Publicidad.objects.filter(activo=True).filter(
        Q(fecha_desde__isnull=True) | Q(fecha_desde__lte=today),
        Q(fecha_hasta__isnull=True) | Q(fecha_hasta__gte=today),
    )


def get_horarios_activos():
    return HorarioAtencion.objects.filter(activo=True)

