import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse

from asociados.services import create_asociado
from comercios.models import ActividadComercial, Comercio
from gestion.permissions import GESTION_COBRAR_CUOTAS
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
    actividad = ActividadComercial.objects.create(nombre="Libreria")
    Comercio.objects.create(
        nombre="Libreria Sur",
        direccion="Mitre 123",
        actividad_comercial=actividad,
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
def test_login_usuario_con_permiso_redirige_a_dashboard_de_gestion(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="admin_gestion",
        password="secreto123",
    )
    permiso = Permission.objects.get(content_type__app_label="gestion", codename="cobrar_cuotas")
    user.user_permissions.add(permiso)

    response = client.post(
        reverse("usuarios:login"),
        {"username": "admin_gestion", "password": "secreto123"},
    )

    assert response.status_code == 302
    assert response.url == reverse("gestion:dashboard")


@pytest.mark.django_db
def test_login_con_asociado_y_permiso_gestion_redirige_a_selector(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="aso_gestion", password="secreto123")
    asociado = create_asociado(
        nombre="Lia",
        apellido="Perez",
        dni="41111999",
        tipo="asociado",
        fecha_alta="2026-05-10",
    )
    asociado.usuario = user
    asociado.save(update_fields=["usuario"])
    permiso = Permission.objects.get(
        content_type__app_label="gestion",
        codename=GESTION_COBRAR_CUOTAS.split(".", 1)[1],
    )
    user.user_permissions.add(permiso)

    response = client.post(
        reverse("usuarios:login"),
        {"username": "aso_gestion", "password": "secreto123"},
    )

    assert response.status_code == 302
    assert response.url == reverse("usuarios:selector_panel")


@pytest.mark.django_db
def test_selector_panel_muestra_experiencias_disponibles(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="selector", password="secreto123")
    asociado = create_asociado(
        nombre="Noa",
        apellido="Rios",
        dni="42111999",
        tipo="asociado",
        fecha_alta="2026-05-10",
    )
    asociado.usuario = user
    asociado.save(update_fields=["usuario"])
    permiso = Permission.objects.get(content_type__app_label="gestion", codename="cobrar_cuotas")
    user.user_permissions.add(permiso)

    client.force_login(user)
    response = client.get(reverse("usuarios:selector_panel"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "Mi cuenta de asociado" in content
    assert "Gestión" in content
