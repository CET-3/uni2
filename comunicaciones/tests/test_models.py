import pytest
from django.db import IntegrityError

from comunicaciones.models import Comunicacion, EntregaComunicacion


@pytest.mark.django_db
def test_comunicacion_y_entrega_tienen_presentacion_y_orden():
    comunicacion = Comunicacion.objects.create(
        tipo="preinscripcion_recibida",
        alcance=Comunicacion.ALCANCE_INDIVIDUAL,
        clave_idempotencia="solicitud:1:recibida:op-1",
        origen_entidad="asociados.SolicitudAsociacion",
        origen_id="1",
    )
    entrega = EntregaComunicacion.objects.create(
        comunicacion=comunicacion,
        canal=EntregaComunicacion.CANAL_EMAIL,
        destino="ana@example.com",
    )

    assert "preinscripcion_recibida" in str(comunicacion)
    assert comunicacion.get_tipo_display() == "Preinscripción recibida"
    assert "ana@example.com" in str(entrega)
    assert entrega.estado == EntregaComunicacion.ESTADO_PENDIENTE


@pytest.mark.django_db(transaction=True)
def test_clave_idempotencia_es_unica():
    datos = {
        "tipo": "preinscripcion_recibida",
        "alcance": Comunicacion.ALCANCE_INDIVIDUAL,
        "clave_idempotencia": "unica",
        "origen_entidad": "asociados.SolicitudAsociacion",
        "origen_id": "1",
    }
    Comunicacion.objects.create(**datos)

    with pytest.raises(IntegrityError):
        Comunicacion.objects.create(**datos)
