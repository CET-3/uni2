from django.db.models import Prefetch

from .models import CategoriaProductoServicio, ProductoServicio


def get_categorias_productos_servicios_publicas():
    productos_publicos = ProductoServicio.objects.filter(activo=True).order_by("orden", "nombre")
    return (
        CategoriaProductoServicio.objects.filter(activa=True)
        .prefetch_related(Prefetch("productos_servicios", queryset=productos_publicos, to_attr="items_publicos"))
        .order_by("orden", "nombre")
    )
