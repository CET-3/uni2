from datetime import date
from decimal import Decimal

import pytest

from asociados.models import Asociado, Colegio, Curso
from asociados.services import create_asociado
from contabilidad.models import CuentaContable
from cuotas.models import Cuota, Pago, PeriodoCuota
from cuotas.services import generar_cuotas_para_periodo, registrar_pago


@pytest.fixture
def asociado_activo():
    colegio = Colegio.objects.create(nombre="CET 3")
    curso = Curso.objects.create(colegio=colegio, nombre="3° 1°")
    return create_asociado(
        nombre="Mia",
        apellido="Acosta",
        dni="36123456",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 3, 10),
        curso_actual=curso,
    )


@pytest.fixture
def periodos():
    marzo = PeriodoCuota.objects.create(
        mes=3, anio=2026, importe=Decimal("3000"), fecha_vencimiento=date(2026, 3, 10)
    )
    abril = PeriodoCuota.objects.create(
        mes=4, anio=2026, importe=Decimal("3000"), fecha_vencimiento=date(2026, 4, 10)
    )
    return marzo, abril


@pytest.fixture
def cuentas_contables():
    CuentaContable.objects.create(
        codigo="1.1.01",
        nombre="Caja",
        tipo=CuentaContable.TIPO_ACTIVO,
    )
    CuentaContable.objects.create(
        codigo="1.1.02",
        nombre="Billetera virtual",
        tipo=CuentaContable.TIPO_ACTIVO,
    )
    CuentaContable.objects.create(
        codigo="4.1.01",
        nombre="Ingresos por cuotas",
        tipo=CuentaContable.TIPO_INGRESO,
    )


@pytest.mark.django_db
def test_generacion_de_cuotas(asociado_activo, periodos):
    creadas = generar_cuotas_para_periodo(periodos[0])
    assert creadas == 1
    assert Cuota.objects.filter(asociado=asociado_activo, periodo=periodos[0]).exists()


@pytest.mark.django_db
def test_no_generar_cuotas_duplicadas(asociado_activo, periodos):
    generar_cuotas_para_periodo(periodos[0])
    creadas = generar_cuotas_para_periodo(periodos[0])
    assert creadas == 0


@pytest.mark.django_db
def test_no_generar_para_inactivos(asociado_activo, periodos):
    asociado_activo.estado = Asociado.ESTADO_INACTIVO
    asociado_activo.save(update_fields=["estado"])
    creadas = generar_cuotas_para_periodo(periodos[0])
    assert creadas == 0


@pytest.mark.django_db
def test_respeta_fecha_inicio_cobro(periodos):
    asociado = create_asociado(
        nombre="Tomi",
        apellido="Leiva",
        dni="37123456",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 3, 20),
    )
    creadas_marzo = generar_cuotas_para_periodo(periodos[0])
    creadas_abril = generar_cuotas_para_periodo(periodos[1])
    assert creadas_marzo == 0
    assert creadas_abril == 1
    assert Cuota.objects.filter(asociado=asociado, periodo=periodos[1]).exists()


@pytest.mark.django_db
def test_pago_completo(asociado_activo, periodos, cuentas_contables):
    generar_cuotas_para_periodo(periodos[0])
    pago = registrar_pago(
        asociado=asociado_activo,
        fecha=date(2026, 3, 5),
        importe=Decimal("3000"),
        metodo=Pago.METODO_EFECTIVO,
    )
    cuota = Cuota.objects.get(asociado=asociado_activo, periodo=periodos[0])
    assert pago.importe == Decimal("3000")
    assert cuota.estado == Cuota.ESTADO_PAGADA


@pytest.mark.django_db
def test_pago_parcial(asociado_activo, periodos, cuentas_contables):
    generar_cuotas_para_periodo(periodos[0])
    registrar_pago(
        asociado=asociado_activo,
        fecha=date(2026, 3, 5),
        importe=Decimal("1000"),
        metodo=Pago.METODO_EFECTIVO,
    )
    cuota = Cuota.objects.get(asociado=asociado_activo, periodo=periodos[0])
    assert cuota.importe_pagado == Decimal("1000")
    assert cuota.estado == Cuota.ESTADO_PARCIAL


@pytest.mark.django_db
def test_aplicacion_a_deuda_mas_antigua(asociado_activo, periodos, cuentas_contables):
    generar_cuotas_para_periodo(periodos[0])
    generar_cuotas_para_periodo(periodos[1])
    pago = registrar_pago(
        asociado=asociado_activo,
        fecha=date(2026, 4, 5),
        importe=Decimal("4000"),
        metodo=Pago.METODO_BILLETERA,
    )
    aplicaciones = list(pago.aplicaciones.order_by("id").values_list("importe", flat=True))
    cuotas = list(Cuota.objects.filter(asociado=asociado_activo).order_by("periodo__mes"))

    assert aplicaciones == [Decimal("3000"), Decimal("1000")]
    assert cuotas[0].estado == Cuota.ESTADO_PAGADA
    assert cuotas[1].estado == Cuota.ESTADO_PARCIAL


@pytest.mark.django_db
def test_rechazo_pagos_superiores_a_deuda(asociado_activo, periodos):
    generar_cuotas_para_periodo(periodos[0])
    with pytest.raises(ValueError, match="superar la deuda"):
        registrar_pago(
            asociado=asociado_activo,
            fecha=date(2026, 3, 5),
            importe=Decimal("5000"),
            metodo=Pago.METODO_EFECTIVO,
        )
