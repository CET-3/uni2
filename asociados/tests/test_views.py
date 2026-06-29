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
def test_panel_asociado_requiere_login(client):
    response = client.get(reverse("asociados:dashboard"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_panel_asociado_responde_con_usuario_vinculado(client):
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
    response = client.get(reverse("asociados:dashboard"))

    assert response.status_code == 200
    assert "Nora" in response.content.decode()


@pytest.mark.django_db
def test_panel_asociado_incluye_secciones_home(client):
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
    response = client.get(reverse("asociados:dashboard"))
    content = response.content.decode()

    assert response.status_code == 200
    assert "Servicios que suman" in content
    assert "Librerías" in content
    assert "20% OFF" in content

