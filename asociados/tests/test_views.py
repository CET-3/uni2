from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from asociados.models import Asociado
from asociados.services import create_asociado


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

