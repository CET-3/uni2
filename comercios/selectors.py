from django.db.models import Count, Prefetch

from .models import ActividadComercial, Comercio


def get_comercio_firmado_queryset():
    return Comercio.objects.filter(
        estado=Comercio.ESTADO_FIRMADO,
    ).select_related("actividad_comercial")


def get_comercios_firmados():
    return get_comercio_firmado_queryset().order_by("orden", "nombre")


def get_rubros_con_comercios():
    comercios_con_foto = Comercio.objects.filter(
        estado=Comercio.ESTADO_FIRMADO,
        foto__isnull=False,
    ).order_by("orden")[:3]

    return (
        ActividadComercial.objects
        .filter(comercios__estado=Comercio.ESTADO_FIRMADO)
        .annotate(cantidad_comercios=Count("comercios"))
        .prefetch_related(
            Prefetch("comercios", queryset=comercios_con_foto, to_attr="comercios_con_foto")
        )
        .order_by("nombre")
    )
