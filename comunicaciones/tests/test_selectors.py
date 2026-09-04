import pytest

from comunicaciones.models import Comunicacion, EntregaComunicacion
from comunicaciones.selectors import listar_entregas_para_origen


@pytest.mark.django_db
def test_listar_entregas_para_origen_no_mezcla_otros_objetos():
    comunicacion_objetivo = Comunicacion.objects.create(
        tipo="preinscripcion_recibida",
        alcance=Comunicacion.ALCANCE_INDIVIDUAL,
        clave_idempotencia="objetivo",
        origen_entidad="asociados.SolicitudAsociacion",
        origen_id="17",
    )
    entrega_objetivo = EntregaComunicacion.objects.create(
        comunicacion=comunicacion_objetivo,
        canal=EntregaComunicacion.CANAL_EMAIL,
        destino="ana@example.com",
    )
    otra_comunicacion = Comunicacion.objects.create(
        tipo="preinscripcion_recibida",
        alcance=Comunicacion.ALCANCE_INDIVIDUAL,
        clave_idempotencia="otra",
        origen_entidad="asociados.SolicitudAsociacion",
        origen_id="18",
    )
    EntregaComunicacion.objects.create(
        comunicacion=otra_comunicacion,
        canal=EntregaComunicacion.CANAL_EMAIL,
        destino="otra@example.com",
    )

    entregas = listar_entregas_para_origen("asociados.SolicitudAsociacion", 17)

    assert list(entregas) == [entrega_objetivo]
    assert entregas[0].comunicacion == comunicacion_objetivo
