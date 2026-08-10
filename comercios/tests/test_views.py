import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from asociados.models import Asociado
from asociados.services import create_asociado
from comercios.models import ActividadComercial, Comercio


@pytest.mark.django_db
def test_validacion_credencial_comercio(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="com2", password="secreto123")
    actividad = ActividadComercial.objects.create(nombre="Papeleria")
    Comercio.objects.create(
        nombre="Papelera Centro",
        direccion="San Martin 55",
        usuario=user,
        actividad_comercial=actividad,
        beneficio_texto="15% en fotocopias",
        estado=Comercio.ESTADO_FIRMADO,
    )
    asociado = create_asociado(
        nombre="Eva",
        apellido="Lopez",
        dni="40333999",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta="2026-05-10",
    )

    client.force_login(user)
    response = client.post(
        reverse("comercios:validar_credencial"),
        {"identificador": str(asociado.token_credencial)},
    )

    assert response.status_code == 200
    assert "Credencial válida" in response.content.decode()


@pytest.mark.django_db
def test_validacion_credencial_comercio_por_dni(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="com-dni", password="secreto123")
    actividad = ActividadComercial.objects.create(nombre="Papelería DNI")
    Comercio.objects.create(
        nombre="Papelera DNI",
        usuario=user,
        actividad_comercial=actividad,
        estado=Comercio.ESTADO_FIRMADO,
    )
    asociado = create_asociado(
        nombre="Nora",
        apellido="Díaz",
        dni="40334001",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta="2026-05-10",
    )
    client.force_login(user)

    response = client.post(
        reverse("comercios:validar_credencial"),
        {"identificador": asociado.dni},
    )

    assert response.status_code == 200
    assert "Credencial válida" in response.content.decode()
    assert "Nora Díaz" in response.content.decode()
