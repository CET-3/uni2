import pytest
from django.urls import reverse

from comercios.models import ActividadComercial, Comercio
from contenidos.models import CategoriaProductoServicio, ProductoServicio, Publicidad


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
def test_home_muestra_publicidades_activas_con_foto_y_links(client):
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
        nombre="Librería Sur",
        direccion="Mitre 123",
        actividad_comercial=actividad,
        beneficio_texto="10% en útiles",
        estado=Comercio.ESTADO_FIRMADO,
    )
    Publicidad.objects.create(
        titulo="Anillado destacado",
        descripcion="Apuntes listos para cursar.",
        etiqueta_principal="Servicio",
        etiqueta_secundaria="Nuevo",
        foto="publicidades/anillado.webp",
        producto_servicio=producto,
        activa=True,
        orden=1,
    )
    Publicidad.objects.create(
        titulo="Librería destacada",
        descripcion="Útiles escolares.",
        etiqueta_principal="Comercio",
        etiqueta_secundaria="10% OFF",
        foto="publicidades/libreria.webp",
        comercio=comercio,
        activa=True,
        orden=2,
    )
    Publicidad.objects.create(
        titulo="Oculta",
        descripcion="No visible.",
        etiqueta_principal="Promo",
        etiqueta_secundaria="OFF",
        foto="publicidades/oculta.webp",
        activa=False,
        orden=3,
    )

    response = client.get(reverse("web:home"))

    contenido = response.content.decode()
    assert "Nuestros favoritos" in contenido
    assert contenido.index("Anillado destacado") < contenido.index("Librería destacada")
    assert "Oculta" not in contenido
    assert "publicidades/anillado.webp" in contenido
    assert reverse("web:producto_servicio_detalle", args=[producto.id]) in contenido
    assert reverse("web:comercio_detalle", args=[comercio.id]) in contenido


@pytest.mark.django_db
def test_detalle_producto_servicio_publico_muestra_producto_activo(client):
    categoria = CategoriaProductoServicio.objects.create(nombre="Impresiones", descripcion="Servicios")
    producto = ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Anillado",
        descripcion="Anillado simple",
        precio_asociados=600,
        precio_no_asociados=900,
        activo=True,
    )

    response = client.get(reverse("web:producto_servicio_detalle", args=[producto.id]))

    contenido = response.content.decode()
    assert response.status_code == 200
    assert "Anillado" in contenido
    assert "$600,00" in contenido


@pytest.mark.django_db
def test_detalle_comercio_publico_muestra_solo_comercio_firmado(client):
    actividad = ActividadComercial.objects.create(nombre="Librería")
    comercio = Comercio.objects.create(
        nombre="Librería Sur",
        direccion="Mitre 123",
        actividad_comercial=actividad,
        beneficio_texto="10% en útiles",
        estado=Comercio.ESTADO_FIRMADO,
    )
    pendiente = Comercio.objects.create(
        nombre="Librería Pendiente",
        direccion="Roca 100",
        actividad_comercial=actividad,
        beneficio_texto="No publicado",
        estado=Comercio.ESTADO_PENDIENTE,
    )

    response = client.get(reverse("web:comercio_detalle", args=[comercio.id]))
    response_pendiente = client.get(reverse("web:comercio_detalle", args=[pendiente.id]))

    contenido = response.content.decode()
    assert response.status_code == 200
    assert "Librería Sur" in contenido
    assert "10% en útiles" in contenido
    assert response_pendiente.status_code == 404


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


@pytest.mark.django_db
def test_categoria_detalle_muestra_sus_productos_activos(client):
    categoria = CategoriaProductoServicio.objects.create(
        nombre="Fotocopias",
        descripcion="Servicios de impresión",
        etiqueta_icono="printer",
        texto_cta="Consultá en la mutual",
        activa=True,
        orden=1,
    )
    ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Fotocopia simple",
        descripcion="ByN",
        precio_asociados=50,
        precio_no_asociados=80,
        activo=True,
        orden=1,
    )
    ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Inactivo",
        descripcion="No visible",
        precio_asociados=100,
        precio_no_asociados=150,
        activo=False,
        orden=2,
    )

    url = reverse("web:categoria_detalle", args=[categoria.pk])
    response = client.get(url)

    assert response.status_code == 200
    assert response.template_name == ["web/categoria_detalle.html"]
    contenido = response.content.decode()
    assert "Fotocopias" in contenido
    assert "Fotocopia simple" in contenido
    assert "Inactivo" not in contenido
    assert "$50,00" in contenido
    assert "Consultá en la mutual" in contenido


@pytest.mark.django_db
def test_categoria_detalle_404_si_inactiva_o_inexistente(client):
    categoria = CategoriaProductoServicio.objects.create(
        nombre="Oculta",
        descripcion="No visible",
        activa=False,
    )

    response = client.get(reverse("web:categoria_detalle", args=[categoria.pk]))
    assert response.status_code == 404

    response = client.get(reverse("web:categoria_detalle", args=[999]))
    assert response.status_code == 404
