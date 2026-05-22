from django.db.models import Q
from django.utils import timezone

from .models import BeneficioComercio, Comercio


def get_comercios_activos():
    return Comercio.objects.filter(activo=True).order_by("nombre")


def get_beneficios_vigentes():
    today = timezone.localdate()
    return BeneficioComercio.objects.filter(
        activo=True,
        comercio__activo=True,
    ).filter(
        Q(fecha_desde__isnull=True) | Q(fecha_desde__lte=today),
        Q(fecha_hasta__isnull=True) | Q(fecha_hasta__gte=today),
    )
