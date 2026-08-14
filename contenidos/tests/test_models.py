from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from contenidos.models import CategoriaProductoServicio, ProductoServicio


@pytest.fixture
def categoria(db):
    return CategoriaProductoServicio.objects.create(nombre="Uniformes")


def crear_producto(categoria, **cambios):
    datos = {
        "categoria": categoria,
        "nombre": "Remera institucional",
        "descripcion": "Remera de la escuela.",
        "precio_asociados": Decimal("9000"),
        "precio_no_asociados": Decimal("12000"),
    }
    datos.update(cambios)
    return ProductoServicio(**datos)


@pytest.mark.parametrize(
    ("es_servicio", "precio_asociados", "precio_no_asociados", "esperado"),
    [
        (False, Decimal("100"), Decimal("150"), "diferenciado"),
        (False, Decimal("100"), Decimal("100"), "unico"),
        (False, Decimal("100"), None, "solo_asociados"),
        (True, None, None, "sin_precio"),
    ],
)
def test_producto_clasifica_tipo_precio(
    categoria,
    es_servicio,
    precio_asociados,
    precio_no_asociados,
    esperado,
):
    producto = crear_producto(
        categoria,
        es_servicio=es_servicio,
        precio_asociados=precio_asociados,
        precio_no_asociados=precio_no_asociados,
    )

    assert producto.tipo_precio == esperado


def test_producto_rechaza_precio_solo_para_no_asociados(categoria):
    producto = crear_producto(categoria, precio_asociados=None, precio_no_asociados=100)

    with pytest.raises(ValidationError) as error:
        producto.full_clean()

    assert error.value.message_dict["precio_asociados"] == ["Debe indicar un precio para asociados."]


def test_producto_rechaza_producto_sin_precio(categoria):
    producto = crear_producto(categoria, precio_asociados=None, precio_no_asociados=None)

    with pytest.raises(ValidationError) as error:
        producto.full_clean()

    assert error.value.message_dict["precio_asociados"] == ["Debe indicar un precio para asociados."]


@pytest.mark.parametrize("campo", ["precio_asociados", "precio_no_asociados"])
def test_producto_rechaza_importes_cero(categoria, campo):
    producto = crear_producto(categoria, **{campo: 0})

    with pytest.raises(ValidationError) as error:
        producto.full_clean()

    assert campo in error.value.message_dict


def test_servicio_acepta_ambos_precios_vacios(categoria):
    servicio = crear_producto(
        categoria,
        es_servicio=True,
        precio_asociados=None,
        precio_no_asociados=None,
    )

    servicio.full_clean()


def test_producto_acepta_ciclo_sin_curso(categoria):
    producto = crear_producto(categoria, ciclo_destinatario="CB")

    producto.full_clean()


def test_producto_acepta_ciclo_con_curso(categoria):
    producto = crear_producto(categoria, ciclo_destinatario="CB", curso_destinatario="1ro")

    producto.full_clean()


def test_producto_rechaza_curso_sin_ciclo(categoria):
    producto = crear_producto(categoria, curso_destinatario="1ro")

    with pytest.raises(ValidationError) as error:
        producto.full_clean()

    assert "curso_destinatario" in error.value.message_dict


def test_categoria_acepta_imagen_informativa_con_titulo(db):
    categoria = CategoriaProductoServicio(
        nombre="Uniformes",
        titulo_imagen_informativa="Tabla de talles",
        imagen_informativa=SimpleUploadedFile("talles.png", b"imagen", content_type="image/png"),
    )

    categoria.full_clean()


def test_categoria_rechaza_imagen_sin_titulo(db):
    categoria = CategoriaProductoServicio(
        nombre="Uniformes",
        imagen_informativa=SimpleUploadedFile("talles.png", b"imagen", content_type="image/png"),
    )

    with pytest.raises(ValidationError) as error:
        categoria.full_clean()

    assert "titulo_imagen_informativa" in error.value.message_dict


def test_categoria_rechaza_titulo_sin_imagen(db):
    categoria = CategoriaProductoServicio(
        nombre="Uniformes",
        titulo_imagen_informativa="Tabla de talles",
    )

    with pytest.raises(ValidationError) as error:
        categoria.full_clean()

    assert "imagen_informativa" in error.value.message_dict
