import pytest

from contenidos.models import CategoriaProductoServicio, ProductoServicio
from contenidos.selectors import get_categorias_productos_servicios_publicas


@pytest.mark.django_db
def test_get_categorias_productos_servicios_publicas_solo_activas_con_items_activos():
    categoria_visible = CategoriaProductoServicio.objects.create(
        nombre="Fotocopias",
        descripcion="Servicios de impresión",
        texto_cta="Consultá disponibilidad uni2mutual@gmail.com",
        activa=True,
        orden=1,
    )
    categoria_inactiva = CategoriaProductoServicio.objects.create(
        nombre="Inactiva",
        descripcion="No visible",
        activa=False,
        orden=2,
    )
    ProductoServicio.objects.create(
        categoria=categoria_visible,
        nombre="Anillado",
        descripcion="Anillado simple",
        precio_asociados=1000,
        precio_no_asociados=1500,
        activo=True,
    )
    ProductoServicio.objects.create(
        categoria=categoria_visible,
        nombre="Oculto",
        descripcion="No visible",
        precio_asociados=1000,
        precio_no_asociados=1500,
        activo=False,
    )
    ProductoServicio.objects.create(
        categoria=categoria_inactiva,
        nombre="Producto inactivo",
        descripcion="No visible",
        precio_asociados=1000,
        precio_no_asociados=1500,
        activo=True,
    )

    resultado = list(get_categorias_productos_servicios_publicas())

    assert len(resultado) == 1
    assert resultado[0].nombre == "Fotocopias"
    assert [item.nombre for item in resultado[0].items_publicos] == ["Anillado"]


@pytest.mark.django_db
def test_get_categorias_productos_servicios_publicas_ordenadas_con_items_ordenados():
    segunda = CategoriaProductoServicio.objects.create(nombre="Segunda", descripcion="Segunda", activa=True, orden=2)
    primera = CategoriaProductoServicio.objects.create(nombre="Primera", descripcion="Primera", activa=True, orden=1)
    ProductoServicio.objects.create(
        categoria=primera,
        nombre="Segundo item",
        descripcion="Segundo",
        precio_asociados=1000,
        precio_no_asociados=1500,
        activo=True,
        orden=2,
    )
    ProductoServicio.objects.create(
        categoria=primera,
        nombre="Primer item",
        descripcion="Primero",
        precio_asociados=1000,
        precio_no_asociados=1500,
        activo=True,
        orden=1,
    )
    ProductoServicio.objects.create(
        categoria=segunda,
        nombre="Otro item",
        descripcion="Otro",
        precio_asociados=1000,
        precio_no_asociados=1500,
        activo=True,
        orden=1,
    )

    resultado = list(get_categorias_productos_servicios_publicas())

    assert [categoria.nombre for categoria in resultado] == ["Primera", "Segunda"]
    assert [item.nombre for item in resultado[0].items_publicos] == ["Primer item", "Segundo item"]
