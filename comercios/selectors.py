from django.db.models import Count

from .models import ActividadComercial, Comercio


def get_comercios_firmados():
    return (
        Comercio.objects.filter(estado=Comercio.ESTADO_FIRMADO)
        .select_related("actividad_comercial")
        .order_by("orden", "nombre")
    )


def get_rubros_con_comercios():
    return (
        ActividadComercial.objects
        .filter(comercios__estado=Comercio.ESTADO_FIRMADO)
        .annotate(cantidad_comercios=Count("comercios"))
        .order_by("nombre")
    )
