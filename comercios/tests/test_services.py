from datetime import date

import pytest

from asociados.models import Asociado, CicloLectivo, ClasificacionAdherente
from asociados.services import create_asociado
from comercios.models import ActividadComercial, Comercio
from comercios.services import validar_credencial
from cuotas.models import Cuota, PeriodoCuota


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


def crear_cuota_actual_impaga(asociado):
    ciclo = CicloLectivo.objects.create(anio=2026)
    periodo = PeriodoCuota.objects.create(
        mes=8,
        ciclo_lectivo=ciclo,
        importe="1000.00",
        importe_recargo_mes="0.00",
        importe_recargo_mes_siguiente="0.00",
        fecha_vencimiento=date(2026, 8, 10),
    )
    return Cuota.objects.create(asociado=asociado, periodo=periodo, importe="1000.00")


@pytest.mark.django_db
def test_validacion_de_credencial_activa(asociado, comercio):
    resultado = validar_credencial(comercio=comercio, token=asociado.token_credencial)
    assert resultado["encontrada"] is True
    assert resultado["valida"] is True
    assert resultado["estado_credencial"] == "Activa"
    assert resultado["nombre"] == "Eva"
    assert resultado["tipo"] == "Asociado"
    assert resultado["dni"] == asociado.dni


@pytest.mark.django_db
def test_validacion_manual_de_credencial_por_dni(asociado, comercio):
    resultado = validar_credencial(comercio=comercio, identificador=asociado.dni)

    assert resultado["valida"] is True
    assert resultado["apellido"] == "Cruz"


@pytest.mark.django_db
def test_validacion_muestra_clasificacion_del_adherente(comercio):
    docente = ClasificacionAdherente.objects.get(nombre="Docente")
    adherente = create_asociado(
        nombre="Eva",
        apellido="Cruz",
        dni="38123457",
        tipo=Asociado.TIPO_ADHERENTE,
        clasificacion_adherente=docente,
        fecha_alta=date(2026, 2, 10),
    )

    resultado = validar_credencial(comercio=comercio, token=adherente.token_credencial)

    assert resultado["dato_institucional_etiqueta"] == "Clasificación"
    assert resultado["dato_institucional_valor"] == "Docente"


@pytest.mark.django_db
def test_rechazo_de_credencial_inactiva(asociado, comercio):
    asociado.estado = Asociado.ESTADO_INACTIVO
    asociado.save(update_fields=["estado"])
    resultado = validar_credencial(comercio=comercio, token=asociado.token_credencial)
    assert resultado["encontrada"] is True
    assert resultado["valida"] is False
    assert resultado["estado_credencial"] == "Inactiva"
    assert "motivo" not in resultado


@pytest.mark.django_db
def test_cuota_actual_impaga_inactiva_credencial_desde_el_dia_11_sin_revelar_causa(asociado, comercio):
    crear_cuota_actual_impaga(asociado)

    dia_10 = validar_credencial(
        comercio=comercio,
        token=asociado.token_credencial,
        fecha_referencia=date(2026, 8, 10),
    )
    dia_11 = validar_credencial(
        comercio=comercio,
        token=asociado.token_credencial,
        fecha_referencia=date(2026, 8, 11),
    )

    assert dia_10["valida"] is True
    assert dia_10["estado_credencial"] == "Activa"
    assert dia_11["valida"] is False
    assert dia_11["estado_credencial"] == "Inactiva"
    assert "deuda" not in dia_11
    assert "motivo" not in dia_11


@pytest.mark.django_db
def test_pago_total_reactiva_credencial_en_la_siguiente_validacion(asociado, comercio):
    cuota = crear_cuota_actual_impaga(asociado)
    cuota.importe_pagado = cuota.importe
    cuota.save(update_fields=["importe_pagado"])

    resultado = validar_credencial(
        comercio=comercio,
        token=asociado.token_credencial,
        fecha_referencia=date(2026, 8, 11),
    )

    assert resultado["valida"] is True
    assert resultado["estado_credencial"] == "Activa"


@pytest.mark.django_db
def test_identificador_inexistente_se_informa_como_credencial_invalida(comercio):
    resultado = validar_credencial(comercio=comercio, identificador="99999999")

    assert resultado == {
        "encontrada": False,
        "valida": False,
        "mensaje": "Credencial inválida",
    }


@pytest.mark.django_db
def test_rechazo_de_validacion_para_comercio_sin_convenio_firmado(asociado, comercio):
    comercio.estado = Comercio.ESTADO_PENDIENTE
    comercio.save(update_fields=["estado"])

    with pytest.raises(ValueError, match="convenio firmado"):
        validar_credencial(comercio=comercio, token=asociado.token_credencial)


@pytest.mark.django_db
def test_comercio_guarda_beneficio_como_texto(comercio):
    assert comercio.beneficio_texto == "10% en utiles"
