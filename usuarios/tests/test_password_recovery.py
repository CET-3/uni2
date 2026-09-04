import re
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from django.contrib.auth.tokens import default_token_generator
from django.contrib.staticfiles import finders
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone

from asociados.models import Asociado
from asociados.services import create_asociado
from comunicaciones.models import Comunicacion
from usuarios.services import solicitar_recuperacion_contrasena


@pytest.fixture
def asociado(db):
    return create_asociado(
        nombre="Ana",
        apellido="Flores",
        dni="48123456",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta="2026-09-04",
        email="ana@example.com",
    )


def extraer_ruta_recuperacion(mensaje):
    coincidencia = re.search(
        r"https?://testserver(?P<ruta>/recuperar-contrasena/[^/]+/[^/]+/)",
        mensaje.body,
    )
    assert coincidencia is not None
    return coincidencia.group("ruta")


@pytest.mark.django_db
def test_solicitud_valida_programa_una_comunicacion(asociado):
    cuenta_encontrada = solicitar_recuperacion_contrasena(
        dni="48.123.456",
        email="ANA@example.com",
        ahora=timezone.now(),
    )

    assert cuenta_encontrada is True
    comunicacion = Comunicacion.objects.get(tipo="recuperacion_contrasena")
    assert comunicacion.origen_entidad == "auth.User"
    assert comunicacion.origen_id == str(asociado.usuario_id)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("dni", "email"),
    [
        ("00000000", "ana@example.com"),
        ("48123456", "otra@example.com"),
        ("48123456", ""),
    ],
)
def test_datos_no_recuperables_no_crean_comunicacion(
    asociado,
    dni,
    email,
):
    cuenta_encontrada = solicitar_recuperacion_contrasena(
        dni=dni,
        email=email,
    )

    assert cuenta_encontrada is False
    assert not Comunicacion.objects.exists()


@pytest.mark.django_db
def test_asociado_inactivo_no_puede_recuperar_password(asociado):
    asociado.estado = Asociado.ESTADO_INACTIVO
    asociado.save(update_fields=["estado"])

    solicitar_recuperacion_contrasena(
        dni=asociado.dni,
        email=asociado.email,
    )

    assert not Comunicacion.objects.exists()


@pytest.mark.django_db
def test_usuario_inactivo_no_puede_recuperar_password(asociado):
    asociado.usuario.is_active = False
    asociado.usuario.save(update_fields=["is_active"])

    solicitar_recuperacion_contrasena(
        dni=asociado.dni,
        email=asociado.email,
    )

    assert not Comunicacion.objects.exists()


@pytest.mark.django_db
def test_dni_identifica_la_cuenta_si_el_email_esta_compartido(asociado):
    otro = create_asociado(
        nombre="Berta",
        apellido="Flores",
        dni="49234567",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta="2026-09-04",
        email=asociado.email,
    )

    solicitar_recuperacion_contrasena(
        dni="49.234.567",
        email="ANA@example.com",
    )

    comunicacion = Comunicacion.objects.get(tipo="recuperacion_contrasena")
    assert comunicacion.origen_id == str(otro.usuario_id)


@pytest.mark.django_db
def test_recuperacion_usa_email_del_asociado_y_no_el_del_user(asociado):
    asociado.usuario.email = "anterior@example.com"
    asociado.usuario.save(update_fields=["email"])

    solicitar_recuperacion_contrasena(
        dni=asociado.dni,
        email="anterior@example.com",
    )
    assert not Comunicacion.objects.exists()

    solicitar_recuperacion_contrasena(
        dni=asociado.dni,
        email=asociado.email,
    )
    assert Comunicacion.objects.filter(tipo="recuperacion_contrasena").count() == 1


@pytest.mark.django_db
def test_recuperacion_no_usa_un_email_modificado_mientras_bloquea_la_cuenta(
    asociado,
    monkeypatch,
):
    user_model = asociado.usuario.__class__

    class UsuariosConCambioConcurrente:
        def select_for_update(self):
            return self

        def get(self, **kwargs):
            Asociado.objects.filter(pk=asociado.pk).update(
                email="nuevo@example.com"
            )
            return user_model.objects.get(**kwargs)

    class UserModelSimulado:
        objects = UsuariosConCambioConcurrente()

    monkeypatch.setattr(
        "usuarios.services.get_user_model",
        lambda: UserModelSimulado,
    )

    solicitar_recuperacion_contrasena(
        dni=asociado.dni,
        email="ana@example.com",
    )

    assert not Comunicacion.objects.exists()


@pytest.mark.django_db
def test_cooldown_permite_un_correo_por_cuenta_cada_quince_minutos(asociado):
    ahora = timezone.now()

    solicitar_recuperacion_contrasena(
        dni=asociado.dni,
        email=asociado.email,
        ahora=ahora,
    )
    cuenta_encontrada = solicitar_recuperacion_contrasena(
        dni=asociado.dni,
        email=asociado.email,
        ahora=ahora + timedelta(minutes=14),
    )

    assert cuenta_encontrada is True
    assert Comunicacion.objects.filter(tipo="recuperacion_contrasena").count() == 1


@pytest.mark.django_db
def test_login_ofrece_recuperar_password(client):
    contenido = client.get(reverse("usuarios:login")).content.decode()

    assert reverse("usuarios:recuperar_contrasena") in contenido
    assert 'class="uni2-login-recovery-link"' in contenido
    assert 'class="bi bi-key" aria-hidden="true"' in contenido
    assert "Olvidé mi contraseña" in contenido


def test_css_presenta_recuperacion_como_accion_secundaria():
    css_path = finders.find("css/uni2-design-system.css")
    assert css_path is not None
    css = Path(css_path).read_text(encoding="utf-8")
    inicio = css.index(".uni2-login-recovery-link {")
    bloque = css[inicio : css.index("\n}", inicio)]

    assert "color: var(--color-text-secondary);" in bloque
    assert "text-decoration: none;" in bloque
    assert ".uni2-login-recovery-link:hover" in css
    assert ".uni2-login-recovery-link:focus-visible" in css


def test_formulario_recuperacion_identifica_la_accion_de_envio(client):
    contenido = client.get(
        reverse("usuarios:recuperar_contrasena")
    ).content.decode()

    assert (
        '<i class="bi bi-envelope-arrow-up" aria-hidden="true"></i> '
        "Enviar instrucciones"
    ) in contenido


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("dni", "email"),
    [
        ("49999999", "ana@example.com"),
        ("48123456", "nadie@example.com"),
    ],
)
def test_dni_o_email_inexistente_muestra_error_explicito(
    client,
    asociado,
    dni,
    email,
):
    respuesta = client.post(
        reverse("usuarios:recuperar_contrasena"),
        {"dni": dni, "email": email},
    )

    contenido = respuesta.content.decode()
    assert respuesta.status_code == 200
    assert (
        "No encontramos una cuenta activa con ese DNI y email. "
        "Revisá los datos ingresados."
    ) in contenido
    assert "Solicitud recibida" not in contenido


def test_confirmacion_no_se_puede_abrir_sin_una_solicitud_valida(client):
    respuesta = client.get(reverse("usuarios:recuperacion_solicitada"))

    assert respuesta.status_code == 302
    assert respuesta.url == reverse("usuarios:recuperar_contrasena")


@pytest.mark.django_db
def test_datos_existentes_avanzan_a_la_confirmacion(client, asociado):
    respuesta = client.post(
        reverse("usuarios:recuperar_contrasena"),
        {"dni": asociado.dni, "email": asociado.email},
        follow=True,
    )

    contenido = respuesta.content.decode()
    assert respuesta.redirect_chain[-1][0] == reverse(
        "usuarios:recuperacion_solicitada"
    )
    assert "Solicitud recibida" in contenido
    assert "Encontramos una cuenta activa con esos datos" in contenido


@pytest.mark.django_db(transaction=True)
@override_settings(UNI2_TRANSACTIONAL_EMAIL_MODE="enabled")
def test_enlace_restablece_password_y_no_puede_reutilizarse(client, asociado):
    client.post(
        reverse("usuarios:recuperar_contrasena"),
        {"dni": asociado.dni, "email": asociado.email},
    )
    ruta_token = extraer_ruta_recuperacion(mail.outbox[0])

    redireccion = client.get(ruta_token)
    assert redireccion.status_code == 302
    formulario_url = redireccion.url
    formulario = client.get(formulario_url)
    assert formulario.status_code == 200
    assert formulario.content.decode().count('class="form-control"') == 2
    assert (
        '<i class="bi bi-key" aria-hidden="true"></i> Guardar contraseña'
        in formulario.content.decode()
    )

    respuesta = client.post(
        formulario_url,
        {
            "new_password1": "otra-clave-2026",
            "new_password2": "otra-clave-2026",
        },
        follow=True,
    )

    asociado.usuario.refresh_from_db()
    assert respuesta.redirect_chain[-1][0] == reverse(
        "usuarios:recuperacion_completada"
    )
    assert asociado.usuario.check_password("otra-clave-2026")
    assert client.post(
        reverse("usuarios:login"),
        {"username": asociado.dni, "password": "otra-clave-2026"},
    ).status_code == 302

    enlace_usado = client.get(ruta_token, follow=True)
    assert "Este enlace ya no está disponible" in enlace_usado.content.decode()


@pytest.mark.django_db(transaction=True)
@override_settings(UNI2_TRANSACTIONAL_EMAIL_MODE="enabled")
def test_enlace_alterado_no_permite_cambiar_password(client, asociado):
    client.post(
        reverse("usuarios:recuperar_contrasena"),
        {"dni": asociado.dni, "email": asociado.email},
    )
    ruta_token = extraer_ruta_recuperacion(mail.outbox[0])
    ruta_alterada = f"{ruta_token[:-2]}x/"

    respuesta = client.get(ruta_alterada, follow=True)

    assert respuesta.status_code == 200
    assert "Este enlace ya no está disponible" in respuesta.content.decode()
    assert (
        '<i class="bi bi-envelope" aria-hidden="true"></i> '
        "Solicitar un enlace nuevo"
    ) in respuesta.content.decode()


@pytest.mark.django_db(transaction=True)
@override_settings(UNI2_TRANSACTIONAL_EMAIL_MODE="enabled")
def test_enlace_vence_despues_de_una_hora(client, asociado, monkeypatch):
    creado_en = datetime(2026, 9, 4, 12, 0, 0)
    monkeypatch.setattr(default_token_generator, "_now", lambda: creado_en)
    client.post(
        reverse("usuarios:recuperar_contrasena"),
        {"dni": asociado.dni, "email": asociado.email},
    )
    ruta_token = extraer_ruta_recuperacion(mail.outbox[0])
    monkeypatch.setattr(
        default_token_generator,
        "_now",
        lambda: creado_en + timedelta(hours=1, seconds=1),
    )

    respuesta = client.get(ruta_token, follow=True)

    assert respuesta.status_code == 200
    assert "Este enlace ya no está disponible" in respuesta.content.decode()
