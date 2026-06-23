import pytest
from django.urls import reverse

from comercios.models import ActividadComercial, Comercio
from contenidos.models import CategoriaProductoServicio, ProductoServicio


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url_name",
    [
        "web:home",
        "web:productos_servicios",
        "web:comercios",
    ],
)
def test_paginas_publicas_responden(client, url_name):
    response = client.get(reverse(url_name))
    assert response.status_code == 200


def test_url_beneficios_no_se_mantiene(client):
    response = client.get("/beneficios/")

    assert response.status_code == 404


@pytest.mark.django_db
def test_productos_servicios_publicos_muestran_activos_ordenados_y_cta_linkeable(client):
    categoria = CategoriaProductoServicio.objects.create(
        nombre="Impresiones",
        descripcion="Servicios para estudiantes",
        etiqueta_icono="printer",
        texto_cta="Consultá disponibilidad uni2mutual@gmail.com",
        activa=True,
        orden=1,
    )
    CategoriaProductoServicio.objects.create(
        nombre="Categoria inactiva",
        descripcion="No visible",
        activa=False,
        orden=2,
    )
    ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Tercero",
        descripcion="Visible tercero",
        precio_asociados=600,
        precio_no_asociados=900,
        activo=True,
        orden=3,
    )
    ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Inactivo",
        descripcion="No visible",
        precio_asociados=600,
        precio_no_asociados=900,
        activo=False,
        orden=1,
    )
    ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Primero",
        descripcion="Visible primero",
        precio_asociados=400,
        precio_no_asociados=700,
        activo=True,
        orden=1,
    )
    ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Segundo",
        descripcion="Visible segundo",
        es_servicio=True,
        precio_asociados=500,
        precio_no_asociados=800,
        activo=True,
        orden=2,
    )

    response = client.get(reverse("web:productos_servicios"))

    contenido = response.content.decode()
    assert contenido.index("Primero") < contenido.index("Segundo") < contenido.index("Tercero")
    assert "Inactivo" not in contenido
    assert "Categoria inactiva" not in contenido
    assert "Servicio" in contenido
    assert "$400,00" in contenido
    assert "mailto:uni2mutual@gmail.com" in contenido


@pytest.mark.django_db
def test_comercios_publicos_muestran_actividad_comercial(client):
    actividad = ActividadComercial.objects.create(nombre="Librería")
    Comercio.objects.create(
        nombre="Librería Zeta",
        direccion="Mitre 123",
        actividad_comercial=actividad,
        beneficio_texto="10% en útiles",
        estado=Comercio.ESTADO_FIRMADO,
        orden=1,
    )
    Comercio.objects.create(
        nombre="Librería Alfa",
        direccion="San Martín 55",
        actividad_comercial=actividad,
        beneficio_texto="2x1 en anillados",
        estado=Comercio.ESTADO_FIRMADO,
        orden=2,
    )
    Comercio.objects.create(
        nombre="Librería Pendiente",
        direccion="Roca 100",
        actividad_comercial=actividad,
        beneficio_texto="No publicado",
        estado=Comercio.ESTADO_PENDIENTE,
    )

    response = client.get(reverse("web:comercios"))

    contenido = response.content.decode()
    assert contenido.index("Librería Zeta") < contenido.index("Librería Alfa")
    assert "Actividad:" in contenido
    assert "Librería" in contenido
    assert "Librería Pendiente" not in contenido


def test_comercio_tiene_orden_para_publicacion():
    campo = Comercio._meta.get_field("orden")

    assert campo.verbose_name == "orden"
