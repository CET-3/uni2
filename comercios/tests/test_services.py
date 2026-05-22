from datetime import date, timedelta

import pytest

from asociados.models import Asociado
from asociados.services import create_asociado
from comercios.models import BeneficioComercio, Comercio
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
    return Comercio.objects.create(nombre="Libreria Sur", direccion="Mitre 123", activo=True)


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
def test_beneficios_vigentes(comercio):
    beneficio = BeneficioComercio.objects.create(
        comercio=comercio,
        titulo="10% utiles",
        descripcion="Descuento",
        tipo_descuento=BeneficioComercio.TIPO_PORCENTAJE,
        valor_descuento=10,
        fecha_desde=date.today() - timedelta(days=1),
        fecha_hasta=date.today() + timedelta(days=5),
        activo=True,
    )
    assert beneficio.activo is True


@pytest.mark.django_db
def test_beneficios_vencidos(comercio):
    beneficio = BeneficioComercio.objects.create(
        comercio=comercio,
        titulo="Promo vieja",
        descripcion="Descuento",
        tipo_descuento=BeneficioComercio.TIPO_PROMOCION,
        fecha_hasta=date.today() - timedelta(days=1),
        activo=True,
    )
    assert beneficio.fecha_hasta < date.today()

