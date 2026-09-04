import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse

from asociados.models import Asociado
from asociados.services import create_asociado
from usuarios.roles import ASOCIADO_GROUP


@pytest.mark.django_db
def test_asociado_cambia_password_y_conserva_sesion(client):
    asociado = create_asociado(
        nombre="Ana",
        apellido="Flores",
        dni="48123456",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta="2026-09-04",
    )
    client.force_login(asociado.usuario)

    response = client.post(
        reverse("usuarios:cambiar_contrasena"),
        {
            "old_password": "48123456",
            "new_password1": "nueva-clave-2026",
            "new_password2": "nueva-clave-2026",
        },
        follow=True,
    )

    asociado.usuario.refresh_from_db()
    assert asociado.usuario.check_password("nueva-clave-2026")
    assert not asociado.usuario.check_password("48123456")
    assert response.redirect_chain[-1][0] == reverse(
        "usuarios:cambiar_contrasena_lista"
    )
    assert client.get(reverse("asociados:cuotas")).status_code == 200


@pytest.mark.django_db
def test_password_actual_incorrecta_no_cambia_password(client):
    asociado = create_asociado(
        nombre="Ana",
        apellido="Flores",
        dni="48123456",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta="2026-09-04",
    )
    client.force_login(asociado.usuario)

    response = client.post(
        reverse("usuarios:cambiar_contrasena"),
        {
            "old_password": "incorrecta",
            "new_password1": "nueva-clave-2026",
            "new_password2": "nueva-clave-2026",
        },
    )

    asociado.usuario.refresh_from_db()
    assert response.status_code == 200
    assert asociado.usuario.check_password("48123456")
    assert not asociado.usuario.check_password("nueva-clave-2026")


@pytest.mark.django_db
def test_visitante_debe_ingresar_para_cambiar_password(client):
    cambio_url = reverse("usuarios:cambiar_contrasena")

    response = client.get(cambio_url)

    assert response.status_code == 302
    assert response.url == f"{reverse('usuarios:login')}?next={cambio_url}"


@pytest.mark.django_db
def test_usuario_sin_perfil_asociado_no_puede_cambiar_password(client):
    usuario = get_user_model().objects.create_user(
        username="solo-comercio",
        password="secreto123",
    )
    client.force_login(usuario)

    response = client.get(reverse("usuarios:cambiar_contrasena"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_usuario_con_rol_asociado_sin_vinculo_vuelve_a_la_home(client):
    usuario = get_user_model().objects.create_user(
        username="asociado-sin-vinculo",
        password="secreto123",
    )
    grupo, _ = Group.objects.get_or_create(name=ASOCIADO_GROUP)
    usuario.groups.add(grupo)
    client.force_login(usuario)

    response = client.get(reverse("usuarios:cambiar_contrasena"))

    assert response.status_code == 302
    assert response.url == reverse("web:home")


@pytest.mark.django_db
def test_navbar_ofrece_cambio_password_solamente_al_asociado(client):
    asociado = create_asociado(
        nombre="Ana",
        apellido="Flores",
        dni="48123456",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta="2026-09-04",
    )
    client.force_login(asociado.usuario)

    contenido_asociado = client.get(reverse("web:home")).content.decode()

    assert contenido_asociado.count(reverse("usuarios:cambiar_contrasena")) == 2
    assert "Cambiar contraseña" in contenido_asociado

    usuario_sin_asociado = get_user_model().objects.create_user(
        username="sin-asociado",
        password="secreto123",
    )
    client.force_login(usuario_sin_asociado)

    contenido_otro = client.get(reverse("web:home")).content.decode()

    assert reverse("usuarios:cambiar_contrasena") not in contenido_otro
    assert "Cambiar contraseña" not in contenido_otro


@pytest.mark.django_db
def test_formulario_de_cambio_usa_controles_bootstrap(client):
    asociado = create_asociado(
        nombre="Ana",
        apellido="Flores",
        dni="48123456",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta="2026-09-04",
    )
    client.force_login(asociado.usuario)

    contenido = client.get(
        reverse("usuarios:cambiar_contrasena")
    ).content.decode()

    assert contenido.count('class="form-control"') == 3
    assert "Guardar contraseña" in contenido
    assert (
        '<i class="bi bi-key" aria-hidden="true"></i> Guardar contraseña'
        in contenido
    )
