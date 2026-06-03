from datetime import date

import pytest
from django.core.exceptions import ValidationError

from asociados.models import Asociado
from asociados.services import create_asociado
from comercios.models import ActividadComercial, Comercio
from comercios.services import validar_credencial


@pytest.fixture
def asociado():
    return create_asociado(
        nombre="Eva",
        apellido="Cruz",
        dni="38123456",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 2, 10),
    )


@pytest.fixture
def comercio():
    actividad = ActividadComercial.objects.create(nombre="Libreria")
    return Comercio.objects.create(
        nombre="Libreria Sur",
        direccion="Mitre 123",
        actividad_comercial=actividad,
        beneficio_texto="10% en utiles",
        estado=Comercio.ESTADO_FIRMADO,
    )


@pytest.mark.django_db
def test_validacion_de_credencial_activa(asociado, comercio):
    resultado = validar_credencial(comercio=comercio, token=asociado.token_credencial)
    assert resultado["valida"] is True
    assert resultado["nombre"] == "Eva"


@pytest.mark.django_db
def test_rechazo_de_credencial_inactiva(asociado, comercio):
    asociado.estado = Asociado.ESTADO_INACTIVO
    asociado.save(update_fields=["estado"])
    resultado = validar_credencial(comercio=comercio, token=asociado.token_credencial)
    assert resultado["valida"] is False
    assert resultado["estado"] == Asociado.ESTADO_INACTIVO


@pytest.mark.django_db
def test_rechazo_de_validacion_para_comercio_sin_convenio_firmado(asociado, comercio):
    comercio.estado = Comercio.ESTADO_PENDIENTE
    comercio.save(update_fields=["estado"])

    with pytest.raises(ValueError, match="convenio firmado"):
        validar_credencial(comercio=comercio, token=asociado.token_credencial)


@pytest.mark.django_db
def test_comercio_guarda_beneficio_como_texto(comercio):
    assert comercio.beneficio_texto == "10% en utiles"


@pytest.mark.django_db
def test_comercio_requiere_beneficio_texto():
    actividad = ActividadComercial.objects.create(nombre="Fotocopias")
    comercio = Comercio(
        nombre="Copias Norte",
        direccion="Roca 123",
        actividad_comercial=actividad,
        beneficio_texto="",
    )

    with pytest.raises(ValidationError):
        comercio.full_clean()
