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
        models.Q(fecha_desde__isnull=True) | models.Q(fecha_desde__lte=today),
        models.Q(fecha_hasta__isnull=True) | models.Q(fecha_hasta__gte=today),
    )

