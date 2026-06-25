from datetime import date
from decimal import Decimal

import pytest

from asociados.models import Asociado, CicloLectivo, Curso
from asociados.services import create_asociado
from cuotas.models import Cuota, Pago, PagoCuota, PeriodoCuota
from cuotas.selectors import calcular_estado_cuota, describir_pago


@pytest.fixture
def asociado_activo():
    curso = Curso.objects.create(anio="3ro", curso="1ra", division=Curso.DIVISION_CB, turno=Curso.TURNO_TM)
    return create_asociado(
        nombre="Mia",
        apellido="Acosta",
        dni="36123456",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 3, 10),
        curso_actual=curso,
    )


@pytest.fixture
def cuota_marzo(asociado_activo):
    ciclo, _ = CicloLectivo.objects.get_or_create(anio=2026)
    periodo = PeriodoCuota.objects.create(
        mes=3,
        ciclo_lectivo=ciclo,
        importe=Decimal("3000"),
        importe_recargo_mes=Decimal("500"),
        importe_recargo_mes_siguiente=Decimal("1000"),
        fecha_vencimiento=date(2026, 3, 10),
    )
    return Cuota.objects.create(
        asociado=asociado_activo,
        periodo=periodo,
        importe=periodo.importe,
        importe_recargo_mes=periodo.importe_recargo_mes,
        importe_recargo_mes_siguiente=periodo.importe_recargo_mes_siguiente,
    )


@pytest.mark.django_db
def test_calcula_cuota_pendiente_antes_del_vencimiento(cuota_marzo):
    estado = calcular_estado_cuota(cuota_marzo, date(2026, 3, 5))

    assert estado.estado == Cuota.ESTADO_PENDIENTE
    assert estado.recargo == Decimal("0")
    assert estado.total_exigible == Decimal("3000")
    assert estado.saldo == Decimal("3000")


@pytest.mark.django_db
def test_calcula_cuota_vencida_mismo_mes(cuota_marzo):
    estado = calcular_estado_cuota(cuota_marzo, date(2026, 3, 12))

    assert estado.estado == Cuota.ESTADO_VENCIDA
    assert estado.recargo == Decimal("500")
    assert estado.total_exigible == Decimal("3500")
    assert estado.saldo == Decimal("3500")


@pytest.mark.django_db
def test_calcula_cuota_vencida_mes_siguiente(cuota_marzo):
    estado = calcular_estado_cuota(cuota_marzo, date(2026, 4, 5))

    assert estado.estado == Cuota.ESTADO_VENCIDA
    assert estado.recargo == Decimal("1000")
    assert estado.total_exigible == Decimal("4000")
    assert estado.saldo == Decimal("4000")


@pytest.mark.django_db
def test_calcula_cuota_pagada_si_el_pago_cubre_lo_exigible(cuota_marzo):
    pago = Pago.objects.create(
        asociado=cuota_marzo.asociado,
        fecha=date(2026, 3, 5),
        importe=Decimal("3000"),
        metodo=Pago.METODO_EFECTIVO,
    )
    PagoCuota.objects.create(pago=pago, cuota=cuota_marzo, importe=Decimal("3000"))
    cuota_marzo.importe_pagado = Decimal("3000")
    cuota_marzo.save(update_fields=["importe_pagado"])

    estado = calcular_estado_cuota(cuota_marzo, date(2026, 3, 12))

    assert estado.estado == Cuota.ESTADO_PAGADA
    assert estado.recargo == Decimal("0")
    assert estado.total_exigible == Decimal("3000")
    assert estado.saldo == Decimal("0")


@pytest.mark.django_db
def test_describe_pago_con_cuotas(cuota_marzo):
    pago = Pago.objects.create(
        asociado=cuota_marzo.asociado,
        fecha=date(2026, 3, 5),
        importe=Decimal("3000"),
        metodo=Pago.METODO_EFECTIVO,
    )
    PagoCuota.objects.create(pago=pago, cuota=cuota_marzo, importe=Decimal("3000"))

    resumen = describir_pago(pago)

    assert resumen.pago == pago
    assert resumen.lineas == ["Cuotas: 03/2026"]


@pytest.mark.django_db
def test_describe_pago_con_cuotas_y_donacion(cuota_marzo):
    from cuotas.models import Donacion

    pago = Pago.objects.create(
        asociado=cuota_marzo.asociado,
        fecha=date(2026, 3, 5),
        importe=Decimal("3500"),
        metodo=Pago.METODO_EFECTIVO,
    )
    PagoCuota.objects.create(pago=pago, cuota=cuota_marzo, importe=Decimal("3000"))
    Donacion.objects.create(
        asociado=cuota_marzo.asociado,
        pago=pago,
        importe=Decimal("500"),
        fecha=date(2026, 3, 5),
    )

    resumen = describir_pago(pago)

    assert resumen.lineas == ["Cuotas: 03/2026", "Donación: $500.00"]
