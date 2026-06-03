from .models import Comercio


def get_comercios_firmados():
    return (
        Comercio.objects.filter(estado=Comercio.ESTADO_FIRMADO)
        .select_related("actividad_comercial")
        .order_by("nombre")
    )
