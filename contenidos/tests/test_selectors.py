import pytest
from django.core.exceptions import ValidationError

from comercios.models import ActividadComercial, Comercio
from contenidos.models import CategoriaProductoServicio, ProductoServicio, Publicidad
from contenidos.selectors import get_categorias_productos_servicios_publicas, get_publicidades_home


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


@pytest.mark.django_db
def test_get_publicidades_home_solo_activas_ordenadas_y_con_vinculos():
    categoria = CategoriaProductoServicio.objects.create(nombre="Impresiones", descripcion="Servicios")
    producto = ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Anillado",
        descripcion="Anillado simple",
        precio_asociados=600,
        precio_no_asociados=900,
    )
    actividad = ActividadComercial.objects.create(nombre="Librería")
    comercio = Comercio.objects.create(
        actividad_comercial=actividad,
        nombre="Librería Sur",
        beneficio_texto="10% en útiles",
        estado=Comercio.ESTADO_FIRMADO,
        direccion="Mitre 123",
    )
    Publicidad.objects.create(
        titulo="Oculta",
        descripcion="No visible",
        etiqueta_principal="Promo",
        etiqueta_secundaria="OFF",
        foto="publicidades/oculta.webp",
        activa=False,
        orden=1,
    )
    Publicidad.objects.create(
        titulo="Producto destacado",
        descripcion="Anillado para apuntes",
        etiqueta_principal="Servicio",
        etiqueta_secundaria="Nuevo",
        foto="publicidades/anillado.webp",
        producto_servicio=producto,
        activa=True,
        orden=2,
    )
    Publicidad.objects.create(
        titulo="Comercio destacado",
        descripcion="Librería adherida",
        etiqueta_principal="Comercio",
        etiqueta_secundaria="10% OFF",
        foto="publicidades/libreria.webp",
        comercio=comercio,
        activa=True,
        orden=1,
    )

    resultado = list(get_publicidades_home())

    assert [publicidad.titulo for publicidad in resultado] == ["Comercio destacado", "Producto destacado"]
    assert resultado[0].comercio == comercio
    assert resultado[1].producto_servicio == producto


@pytest.mark.django_db
def test_publicidad_no_puede_vincular_producto_y_comercio_a_la_vez():
    categoria = CategoriaProductoServicio.objects.create(nombre="Impresiones", descripcion="Servicios")
    producto = ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Anillado",
        descripcion="Anillado simple",
        precio_asociados=600,
        precio_no_asociados=900,
    )
    actividad = ActividadComercial.objects.create(nombre="Librería")
    comercio = Comercio.objects.create(
        actividad_comercial=actividad,
        nombre="Librería Sur",
        beneficio_texto="10% en útiles",
        estado=Comercio.ESTADO_FIRMADO,
        direccion="Mitre 123",
    )
    publicidad = Publicidad(
        titulo="Destino doble",
        descripcion="No válido",
        etiqueta_principal="Promo",
        etiqueta_secundaria="OFF",
        foto="publicidades/doble.webp",
        producto_servicio=producto,
        comercio=comercio,
    )

    with pytest.raises(ValidationError, match="no puede estar vinculada"):
        publicidad.full_clean()
