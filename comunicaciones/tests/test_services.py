from unittest.mock import Mock

import pytest
from django.core import mail
from django.test import override_settings

from comunicaciones.models import EntregaComunicacion
from comunicaciones.services import programar_email_transaccional


CONTEXTO = {
    "nombre": "Ana",
    "seguimiento_url": "https://uni2.test/sumate/solicitud/token/",
}


@pytest.mark.django_db(transaction=True)
@override_settings(
    UNI2_TRANSACTIONAL_EMAIL_MODE="enabled",
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="UNI2 <no-responder@uni2.test>",
)
def test_programar_email_envia_html_y_texto_solo_una_vez():
    entrega_1 = programar_email_transaccional(
        tipo="preinscripcion_recibida",
        destino="ana@example.com",
        clave_idempotencia="solicitud:1:recibida:1",
        origen_entidad="asociados.SolicitudAsociacion",
        origen_id=1,
        contexto=CONTEXTO,
    )
    entrega_2 = programar_email_transaccional(
        tipo="preinscripcion_recibida",
        destino="ana@example.com",
        clave_idempotencia="solicitud:1:recibida:1",
        origen_entidad="asociados.SolicitudAsociacion",
        origen_id=1,
        contexto=CONTEXTO,
    )

    entrega_1.refresh_from_db()
    assert entrega_1.pk == entrega_2.pk
    assert entrega_1.estado == EntregaComunicacion.ESTADO_ENVIADA
    assert entrega_1.intentos == 1
    assert len(mail.outbox) == 1
    assert mail.outbox[0].body
    assert mail.outbox[0].alternatives[0].mimetype == "text/html"


@pytest.mark.django_db(transaction=True)
@override_settings(UNI2_TRANSACTIONAL_EMAIL_MODE="disabled")
def test_modo_deshabilitado_registra_entrega_omitida_sin_enviar():
    entrega = programar_email_transaccional(
        tipo="preinscripcion_recibida",
        destino="ana@example.com",
        clave_idempotencia="solicitud:2:recibida:1",
        origen_entidad="asociados.SolicitudAsociacion",
        origen_id=2,
        contexto=CONTEXTO,
    )

    entrega.refresh_from_db()
    assert entrega.estado == EntregaComunicacion.ESTADO_OMITIDA
    assert entrega.intentos == 0
    assert len(mail.outbox) == 0


@pytest.mark.django_db(transaction=True)
@override_settings(
    UNI2_TRANSACTIONAL_EMAIL_MODE="redirect",
    UNI2_TRANSACTIONAL_EMAIL_REDIRECT_TO="uni2.app.cet3@gmail.com",
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL=(
        "UNI2 App — Mutual CET 3 <uni2.app.cet3@gmail.com>"
    ),
)
def test_modo_redirect_conserva_destino_y_envia_solo_a_casilla_segura():
    entrega = programar_email_transaccional(
        tipo="preinscripcion_recibida",
        destino="persona-real@example.com",
        clave_idempotencia="solicitud:redirect:1",
        origen_entidad="asociados.SolicitudAsociacion",
        origen_id=1,
        contexto=CONTEXTO,
    )

    entrega.refresh_from_db()
    assert entrega.destino == "persona-real@example.com"
    assert entrega.estado == EntregaComunicacion.ESTADO_ENVIADA
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["uni2.app.cet3@gmail.com"]
    assert mail.outbox[0].subject.startswith("[STAGING] ")
    assert "persona-real@example.com" not in mail.outbox[0].subject


@pytest.mark.django_db(transaction=True)
@override_settings(
    UNI2_TRANSACTIONAL_EMAIL_MODE="redirect",
    UNI2_TRANSACTIONAL_EMAIL_REDIRECT_TO="",
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
def test_modo_redirect_sin_destino_seguro_falla_sin_enviar_al_original():
    entrega = programar_email_transaccional(
        tipo="preinscripcion_recibida",
        destino="persona-real@example.com",
        clave_idempotencia="solicitud:redirect:incompleto",
        origen_entidad="asociados.SolicitudAsociacion",
        origen_id=2,
        contexto=CONTEXTO,
    )

    entrega.refresh_from_db()
    assert entrega.estado == EntregaComunicacion.ESTADO_FALLIDA
    assert entrega.intentos == 1
    assert "destinatario seguro" in entrega.ultimo_error
    assert "persona-real@example.com" not in entrega.ultimo_error
    assert len(mail.outbox) == 0


@pytest.mark.django_db(transaction=True)
@override_settings(UNI2_TRANSACTIONAL_EMAIL_MODE="enabled")
def test_fallo_del_backend_queda_registrado(monkeypatch):
    monkeypatch.setattr(
        "comunicaciones.services.EmailMultiAlternatives.send",
        Mock(side_effect=OSError("sin conexión")),
    )

    entrega = programar_email_transaccional(
        tipo="preinscripcion_recibida",
        destino="ana@example.com",
        clave_idempotencia="solicitud:3:recibida:1",
        origen_entidad="asociados.SolicitudAsociacion",
        origen_id=3,
        contexto=CONTEXTO,
    )

    entrega.refresh_from_db()
    assert entrega.estado == EntregaComunicacion.ESTADO_FALLIDA
    assert entrega.intentos == 1
    assert "sin conexión" in entrega.ultimo_error


@pytest.mark.django_db(transaction=True)
@override_settings(
    UNI2_TRANSACTIONAL_EMAIL_MODE="enabled",
    EMAIL_HOST_PASSWORD="clave-de-aplicacion-secreta",
)
def test_fallo_del_backend_no_guarda_la_contrasena_smtp(monkeypatch):
    monkeypatch.setattr(
        "comunicaciones.services.EmailMultiAlternatives.send",
        Mock(
            side_effect=OSError(
                "autenticación rechazada: clave-de-aplicacion-secreta"
            )
        ),
    )

    entrega = programar_email_transaccional(
        tipo="preinscripcion_recibida",
        destino="ana@example.com",
        clave_idempotencia="solicitud:4:recibida:1",
        origen_entidad="asociados.SolicitudAsociacion",
        origen_id=4,
        contexto=CONTEXTO,
    )

    entrega.refresh_from_db()
    assert entrega.estado == EntregaComunicacion.ESTADO_FALLIDA
    assert "clave-de-aplicacion-secreta" not in entrega.ultimo_error
    assert "[secreto oculto]" in entrega.ultimo_error
