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
