from django.db.models import Prefetch, Q

from comercios.models import Comercio
from .models import CategoriaProductoServicio, ProductoServicio, Publicidad


def get_categorias_productos_servicios_publicas():
    productos_publicos = ProductoServicio.objects.filter(activo=True).order_by("orden", "nombre")
    return (
        CategoriaProductoServicio.objects.filter(activa=True)
        .prefetch_related(Prefetch("productos_servicios", queryset=productos_publicos, to_attr="items_publicos"))
        .order_by("orden", "nombre")
    )


def get_publicidades_home():
    return (
        Publicidad.objects.filter(activa=True)
        .filter(Q(comercio__isnull=True) | Q(comercio__estado=Comercio.ESTADO_FIRMADO))
        .select_related("producto_servicio", "producto_servicio__categoria", "comercio", "comercio__actividad_comercial")
        .order_by("orden", "titulo")
    )
