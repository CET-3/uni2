from decimal import Decimal
from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from asociados.models import Asociado
from asociados.services import create_asociado
from comercios.models import ActividadComercial, Comercio
from contenidos.models import CategoriaProductoServicio, ProductoServicio, Publicidad


@pytest.mark.django_db
def test_ruta_anterior_del_panel_asociado_fue_retirada(client):
    response = client.get("/asociado/panel/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_home_asociado_responde_con_usuario_vinculado(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="aso2", password="secreto123")
    asociado = create_asociado(
        nombre="Nora",
        apellido="Diaz",
        dni="40222999",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 5, 10),
    )
    asociado.usuario = user
    asociado.save(update_fields=["usuario"])

    client.force_login(user)
    response = client.get(reverse("web:home"))

    assert response.status_code == 200
    assert "Nora" in response.content.decode()


@pytest.mark.django_db
def test_home_asociado_incluye_secciones_publicas(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="aso3", password="secreto123")
    asociado = create_asociado(
        nombre="Leo",
        apellido="Messi",
        dni="40223000",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 5, 10),
    )
    asociado.usuario = user
    asociado.save(update_fields=["usuario"])

    categoria = CategoriaProductoServicio.objects.create(nombre="Impresiones", etiqueta_icono="printer")
    ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Fotocopias",
        descripcion="Fotocopias rápidas y de excelente calidad.",
        precio_asociados=Decimal("10.00"),
        precio_no_asociados=Decimal("20.00"),
    )

    rubro = ActividadComercial.objects.create(nombre="Librerías")
    comercio = Comercio.objects.create(
        nombre="Librería Centro",
        actividad_comercial=rubro,
        estado=Comercio.ESTADO_FIRMADO,
    )
    Publicidad.objects.create(
        titulo="20% OFF",
        descripcion="Descuento exclusivo",
        etiqueta_principal="Imperdible",
        etiqueta_secundaria="En librería",
        activa=True,
    )

    client.force_login(user)
    response = client.get(reverse("web:home"))
    content = response.content.decode()

    assert response.status_code == 200
    assert "Servicios que suman" in content
    assert "Librerías" in content
    assert "20% OFF" in content


@pytest.mark.django_db
@pytest.mark.parametrize("url_name", ["asociados:credencial", "asociados:cuotas"])
def test_pantallas_asociado_usan_contenedor_sin_familias_paralelas(client, url_name):
    asociado = create_asociado(
        nombre="Nora",
        apellido="Diseño",
        dni="40999111",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 8, 1),
    )
    client.force_login(asociado.usuario)

    content = client.get(reverse(url_name)).content.decode()

    assert 'class="container py-5' in content
    assert "uni2-member-" not in content
    assert "uni2-ops-" not in content


@pytest.mark.django_db
def test_cuotas_asociado_usan_metricas_y_superficie_compartidas(client):
    asociado = create_asociado(
        nombre="Leo",
        apellido="Cuotas",
        dni="40999222",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 8, 1),
    )
    client.force_login(asociado.usuario)

    content = client.get(reverse("asociados:cuotas")).content.decode()

    assert "uni2-metric-card" in content
    assert "uni2-surface-card" in content
