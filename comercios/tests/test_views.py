import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from asociados.models import Asociado
from asociados.services import create_asociado
from comercios.models import Comercio


@pytest.mark.django_db
def test_validacion_credencial_comercio(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="com2", password="secreto123")
    Comercio.objects.create(nombre="Papelera Centro", direccion="San Martin 55", usuario=user)
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
        {"token": str(asociado.token_credencial)},
    )

    assert response.status_code == 200
    assert "Credencial valida" in response.content.decode()
