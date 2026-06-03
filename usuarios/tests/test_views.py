import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse

from asociados.services import create_asociado
from comercios.models import Comercio
from usuarios.services import COMERCIO_GROUP


@pytest.mark.django_db
def test_login_redirige_a_panel_asociado(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="aso", password="secreto123")
    asociado = create_asociado(
        nombre="Ana",
        apellido="Perez",
        dni="40111999",
        tipo="asociado",
        fecha_alta="2026-05-10",
    )
    asociado.usuario = user
    asociado.save(update_fields=["usuario"])

    response = client.post(
        reverse("usuarios:login"),
        {"username": "aso", "password": "secreto123"},
    )

    assert response.status_code == 302
    assert response.url == reverse("asociados:dashboard")


@pytest.mark.django_db
def test_login_redirige_a_panel_comercio(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="com", password="secreto123")
    Comercio.objects.create(
        nombre="Libreria Sur",
        direccion="Mitre 123",
        beneficio_texto="10% en utiles",
        usuario=user,
    )

    response = client.post(
        reverse("usuarios:login"),
        {"username": "com", "password": "secreto123"},
    )

    assert response.status_code == 302
    assert response.url == reverse("comercios:dashboard")


@pytest.mark.django_db
def test_login_usuario_con_grupo_comercio_sin_perfil_redirige_a_home(client):
    group = Group.objects.create(name=COMERCIO_GROUP)
    user_model = get_user_model()
    user = user_model.objects.create_user(username="com_sin_perfil", password="secreto123")
    user.groups.add(group)

    response = client.post(
        reverse("usuarios:login"),
        {"username": "com_sin_perfil", "password": "secreto123"},
    )

    assert response.status_code == 302
    assert response.url == reverse("web:home")


@pytest.mark.django_db
def test_login_staff_redirige_a_dashboard_de_gestion(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="admin_gestion",
        password="secreto123",
        is_staff=True,
    )

    response = client.post(
        reverse("usuarios:login"),
        {"username": "admin_gestion", "password": "secreto123"},
    )

    assert response.status_code == 302
    assert response.url == reverse("gestion:dashboard")
