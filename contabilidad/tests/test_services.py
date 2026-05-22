from datetime import date
from decimal import Decimal

import pytest

from asociados.models import Asociado, Colegio, Curso
from asociados.services import create_asociado
from contabilidad.models import Asiento, CuentaContable, PartidaAsiento
from contabilidad.services import validar_asiento
from cuotas.models import Pago, PeriodoCuota
from cuotas.services import generar_cuotas_para_periodo, registrar_pago


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


@pytest.fixture
def asociado_con_cuota():
    colegio = Colegio.objects.create(nombre="CET 3")
    curso = Curso.objects.create(colegio=colegio, nombre="4° 1°")
    asociado = create_asociado(
        nombre="Nora",
        apellido="Vega",
        dni="39123456",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 3, 10),
        curso_actual=curso,
    )
    periodo = PeriodoCuota.objects.create(
        mes=3,
        anio=2026,
        importe=Decimal("3000"),
        fecha_vencimiento=date(2026, 3, 10),
    )
    generar_cuotas_para_periodo(periodo)
    return asociado


@pytest.mark.django_db
def test_registrar_pago_crea_asiento_balanceado(asociado_con_cuota, cuentas_contables):
    pago = registrar_pago(
        asociado=asociado_con_cuota,
        fecha=date(2026, 3, 5),
        importe=Decimal("3000"),
        metodo=Pago.METODO_EFECTIVO,
    )

    asiento = Asiento.objects.get(origen_object_id=pago.id)
    partidas = list(asiento.partidas.order_by("id"))

    assert asiento.importe == Decimal("3000")
    assert len(partidas) == 2
    assert partidas[0].movimiento == PartidaAsiento.MOVIMIENTO_DEBE
    assert partidas[0].cuenta.codigo == "1.1.01"
    assert partidas[1].movimiento == PartidaAsiento.MOVIMIENTO_HABER
    assert partidas[1].cuenta.codigo == "4.1.01"
    debe, haber = asiento.get_totales_partidas()
    assert debe == Decimal("3000")
    assert haber == Decimal("3000")


@pytest.mark.django_db
def test_validar_asiento_rechaza_menos_de_dos_partidas(cuentas_contables):
    cuenta = CuentaContable.objects.get(codigo="1.1.01")
    asiento = Asiento.objects.create(
        fecha=date(2026, 3, 5),
        descripcion="Asiento incompleto",
        tipo=Asiento.TIPO_INGRESO,
        importe=Decimal("3000"),
    )
    PartidaAsiento.objects.create(
        asiento=asiento,
        cuenta=cuenta,
        movimiento=PartidaAsiento.MOVIMIENTO_DEBE,
        importe=Decimal("3000"),
    )

    with pytest.raises(ValueError, match="al menos 2 partidas"):
        validar_asiento(asiento)


@pytest.mark.django_db
def test_validar_asiento_rechaza_desbalance(cuentas_contables):
    caja = CuentaContable.objects.get(codigo="1.1.01")
    ingresos = CuentaContable.objects.get(codigo="4.1.01")
    asiento = Asiento.objects.create(
        fecha=date(2026, 3, 5),
        descripcion="Asiento desbalanceado",
        tipo=Asiento.TIPO_INGRESO,
        importe=Decimal("3000"),
    )
    PartidaAsiento.objects.bulk_create(
        [
            PartidaAsiento(
                asiento=asiento,
                cuenta=caja,
                movimiento=PartidaAsiento.MOVIMIENTO_DEBE,
                importe=Decimal("3000"),
            ),
            PartidaAsiento(
                asiento=asiento,
                cuenta=ingresos,
                movimiento=PartidaAsiento.MOVIMIENTO_HABER,
                importe=Decimal("2500"),
            ),
        ]
    )

    with pytest.raises(ValueError, match="debe y haber deben coincidir"):
        validar_asiento(asiento)


@pytest.mark.django_db
def test_validar_asiento_admite_mas_de_dos_partidas_balanceadas(cuentas_contables):
    caja = CuentaContable.objects.get(codigo="1.1.01")
    billetera = CuentaContable.objects.get(codigo="1.1.02")
    ingresos = CuentaContable.objects.get(codigo="4.1.01")
    asiento = Asiento.objects.create(
        fecha=date(2026, 3, 5),
        descripcion="Asiento con multiples partidas",
        tipo=Asiento.TIPO_INGRESO,
        importe=Decimal("3000"),
    )
    PartidaAsiento.objects.bulk_create(
        [
            PartidaAsiento(
                asiento=asiento,
                cuenta=caja,
                movimiento=PartidaAsiento.MOVIMIENTO_DEBE,
                importe=Decimal("1000"),
            ),
            PartidaAsiento(
                asiento=asiento,
                cuenta=billetera,
                movimiento=PartidaAsiento.MOVIMIENTO_DEBE,
                importe=Decimal("2000"),
            ),
            PartidaAsiento(
                asiento=asiento,
                cuenta=ingresos,
                movimiento=PartidaAsiento.MOVIMIENTO_HABER,
                importe=Decimal("3000"),
            ),
        ]
    )

    assert validar_asiento(asiento) == asiento


@pytest.mark.django_db
def test_registrar_pago_falla_si_faltan_cuentas_contables(asociado_con_cuota):
    with pytest.raises(ValueError, match="Faltan cuentas contables iniciales"):
        registrar_pago(
            asociado=asociado_con_cuota,
            fecha=date(2026, 3, 5),
            importe=Decimal("3000"),
            metodo=Pago.METODO_EFECTIVO,
        )
