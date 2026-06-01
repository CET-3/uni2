from .models import Comercio


def get_comercios_firmados():
    return (
        Comercio.objects.filter(estado=Comercio.ESTADO_FIRMADO)
        .select_related("actividad_comercial")
        .order_by("nombre")
    )


def get_comercios_con_beneficio():
    return (
        Comercio.objects.filter(
            estado=Comercio.ESTADO_FIRMADO,
            beneficio_texto__isnull=False,
        )
        .exclude(beneficio_texto="")
        .order_by("nombre")
    )
