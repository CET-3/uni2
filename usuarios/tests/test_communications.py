import uuid
from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings

from asociados.models import Asociado
from comunicaciones.models import Comunicacion, EntregaComunicacion
from usuarios.communications import (
    programar_correo_alta_usuario,
    programar_correo_recuperacion_contrasena,
)


@pytest.fixture
def asociado_con_usuario(db):
    usuario = get_user_model().objects.create_user(
        username="48123456",
        password="48123456",
        email="ana@example.com",
        first_name="Ana",
        last_name="Flores",
    )
    return Asociado.objects.create(
        usuario=usuario,
        nombre="Ana",
        apellido="Flores",
        dni="48123456",
        email="ana@example.com",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 9, 4),
        fecha_inicio_cobro=date(2026, 7, 1),
    )


@pytest.mark.django_db(transaction=True)
@override_settings(
    UNI2_TRANSACTIONAL_EMAIL_MODE="enabled",
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    UNI2_SITE_URL="https://uni2.example",
)
def test_programar_correo_alta_informa_credenciales_y_login(
    asociado_con_usuario,
):
    entrega = programar_correo_alta_usuario(
        asociado=asociado_con_usuario,
        usuario=asociado_con_usuario.usuario,
    )

    entrega.refresh_from_db()
    mensaje = mail.outbox[0]
    assert entrega.comunicacion.tipo == "alta_usuario"
    assert entrega.destino == "ana@example.com"
    assert mensaje.to == ["ana@example.com"]
    assert "48123456" in mensaje.body
    assert "https://uni2.example/login/" in mensaje.body
    assert "cambiar" in mensaje.body.lower()
    assert "48123456" not in mensaje.subject
    assert "ana@example.com" not in mensaje.subject
    assert "Ana" not in mensaje.subject


@pytest.mark.django_db
def test_programar_correo_alta_sin_email_no_crea_comunicacion(
    asociado_con_usuario,
):
    asociado_con_usuario.email = ""
    asociado_con_usuario.save(update_fields=["email"])

    entrega = programar_correo_alta_usuario(
        asociado=asociado_con_usuario,
        usuario=asociado_con_usuario.usuario,
    )

    assert entrega is None
    assert not Comunicacion.objects.exists()


@pytest.mark.django_db(transaction=True)
@override_settings(
    UNI2_TRANSACTIONAL_EMAIL_MODE="enabled",
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    UNI2_SITE_URL="https://uni2.example",
)
def test_correo_alta_es_idempotente_por_asociado(asociado_con_usuario):
    primera_entrega = programar_correo_alta_usuario(
        asociado=asociado_con_usuario,
        usuario=asociado_con_usuario.usuario,
    )
    segunda_entrega = programar_correo_alta_usuario(
        asociado=asociado_con_usuario,
        usuario=asociado_con_usuario.usuario,
    )

    assert segunda_entrega.pk == primera_entrega.pk
    assert Comunicacion.objects.count() == 1
    assert EntregaComunicacion.objects.count() == 1
    assert len(mail.outbox) == 1


@pytest.mark.django_db(transaction=True)
@override_settings(
    UNI2_TRANSACTIONAL_EMAIL_MODE="enabled",
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
def test_correo_recuperacion_contiene_token_sin_persistirlo(
    asociado_con_usuario,
):
    recuperacion_url = (
        "https://uni2.example/recuperar-contrasena/MQ/token-privado/"
    )

    entrega = programar_correo_recuperacion_contrasena(
        asociado=asociado_con_usuario,
        usuario=asociado_con_usuario.usuario,
        recuperacion_url=recuperacion_url,
        operacion_id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
    )

    mensaje = mail.outbox[0]
    assert recuperacion_url in mensaje.body
    assert "una hora" in mensaje.body.lower()
    assert "token-privado" not in str(Comunicacion.objects.values().get())
    assert entrega.comunicacion.tipo == "recuperacion_contrasena"
    assert "48123456" not in mensaje.subject
    assert "ana@example.com" not in mensaje.subject
    assert "Ana" not in mensaje.subject
