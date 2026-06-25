from datetime import date
from decimal import Decimal

import pytest

from asociados.models import Asociado, CicloLectivo, Curso
from asociados.services import create_asociado
from cuotas.models import Cuota, Donacion, Pago, PeriodoCuota
from cuotas.services import (
    generar_cuotas_iniciales_para_asociado,
    generar_cuotas_para_periodo,
    registrar_pago,
)


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
def periodos():
    ciclo, _ = CicloLectivo.objects.get_or_create(anio=2026)
    marzo = PeriodoCuota.objects.create(
        mes=3,
        ciclo_lectivo=ciclo,
        importe=Decimal("3000"),
        importe_recargo_mes=Decimal("500"),
        importe_recargo_mes_siguiente=Decimal("500"),
        fecha_vencimiento=date(2026, 3, 10),
    )
    abril = PeriodoCuota.objects.create(
        mes=4,
        ciclo_lectivo=ciclo,
        importe=Decimal("3000"),
        importe_recargo_mes=Decimal("500"),
        importe_recargo_mes_siguiente=Decimal("500"),
        fecha_vencimiento=date(2026, 4, 10),
    )
    return marzo, abril


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
def test_pago_completo(asociado_activo, periodos):
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
    assert cuota.importe_recargo_mes == Decimal("500")


@pytest.mark.django_db
def test_rechaza_pago_menor_a_deuda(asociado_activo, periodos):
    generar_cuotas_para_periodo(periodos[0])
    with pytest.raises(ValueError, match="menor a la deuda"):
        registrar_pago(
            asociado=asociado_activo,
            fecha=date(2026, 3, 5),
            importe=Decimal("1000"),
            metodo=Pago.METODO_EFECTIVO,
        )


@pytest.mark.django_db
def test_aplicacion_a_deuda_mas_antigua(asociado_activo, periodos):
    generar_cuotas_para_periodo(periodos[0])
    generar_cuotas_para_periodo(periodos[1])
    pago = registrar_pago(
        asociado=asociado_activo,
        fecha=date(2026, 4, 5),
        importe=Decimal("7000"),
        metodo=Pago.METODO_BILLETERA,
    )
    aplicaciones = list(pago.aplicaciones.order_by("id").values_list("importe", flat=True))
    cuotas = list(Cuota.objects.filter(asociado=asociado_activo).order_by("periodo__mes"))

    assert aplicaciones == [Decimal("4000"), Decimal("3000")]
    assert cuotas[0].estado == Cuota.ESTADO_PAGADA
    assert cuotas[1].estado == Cuota.ESTADO_PAGADA


@pytest.mark.django_db
def test_pago_de_cuotas_seleccionadas_deja_cuotas_posteriores_pendientes(asociado_activo, periodos):
    generar_cuotas_para_periodo(periodos[0])
    generar_cuotas_para_periodo(periodos[1])
    cuota_marzo, cuota_abril = Cuota.objects.filter(asociado=asociado_activo).order_by("periodo__mes")

    pago = registrar_pago(
        asociado=asociado_activo,
        fecha=date(2026, 4, 5),
        importe=Decimal("4000"),
        metodo=Pago.METODO_EFECTIVO,
        cuotas_ids=[cuota_marzo.id],
    )

    cuota_marzo.refresh_from_db()
    cuota_abril.refresh_from_db()
    assert pago.importe == Decimal("4000")
    assert list(pago.aplicaciones.values_list("cuota_id", flat=True)) == [cuota_marzo.id]
    assert cuota_marzo.estado == Cuota.ESTADO_PAGADA
    assert cuota_abril.estado == Cuota.ESTADO_PENDIENTE


@pytest.mark.django_db
def test_rechaza_seleccion_que_salta_cuota_mas_vieja(asociado_activo, periodos):
    generar_cuotas_para_periodo(periodos[0])
    generar_cuotas_para_periodo(periodos[1])
    cuota_marzo, cuota_abril = Cuota.objects.filter(asociado=asociado_activo).order_by("periodo__mes")

    with pytest.raises(ValueError, match="deuda más antigua"):
        registrar_pago(
            asociado=asociado_activo,
            fecha=date(2026, 4, 5),
            importe=Decimal("3000"),
            metodo=Pago.METODO_EFECTIVO,
            cuotas_ids=[cuota_abril.id],
        )

    cuota_marzo.refresh_from_db()
    cuota_abril.refresh_from_db()
    assert Pago.objects.count() == 0
    assert cuota_marzo.estado == Cuota.ESTADO_PENDIENTE
    assert cuota_abril.estado == Cuota.ESTADO_PENDIENTE


@pytest.mark.django_db
def test_pago_mayor_a_deuda_genera_donacion(asociado_activo, periodos):
    generar_cuotas_para_periodo(periodos[0])
    pago = registrar_pago(
        asociado=asociado_activo,
        fecha=date(2026, 3, 5),
        importe=Decimal("3500"),
        metodo=Pago.METODO_EFECTIVO,
    )
    cuota = Cuota.objects.get(asociado=asociado_activo, periodo=periodos[0])
    assert cuota.importe_pagado == Decimal("3000")
    assert cuota.estado == Cuota.ESTADO_PAGADA
    assert pago.importe == Decimal("3500")

    donacion = Donacion.objects.get(pago=pago)
    assert donacion.importe == Decimal("500")


@pytest.mark.django_db
def test_pago_fuera_de_termino_aplica_recargo_mes(asociado_activo, periodos):
    generar_cuotas_para_periodo(periodos[0])

    pago = registrar_pago(
        asociado=asociado_activo,
        fecha=date(2026, 3, 12),
        importe=Decimal("3500"),
        metodo=Pago.METODO_EFECTIVO,
    )
    cuota = Cuota.objects.get(asociado=asociado_activo, periodo=periodos[0])

    assert pago.importe == Decimal("3500")
    assert cuota.importe_pagado == Decimal("3500")
    assert cuota.estado == Cuota.ESTADO_PAGADA


@pytest.mark.django_db
def test_recargo_escalonado_mes_anterior_aplica_recargo_mayor(asociado_activo, periodos):
    """Pagar en abril una cuota de marzo vencida: aplica recargo_mes + recargo_mes_siguiente."""
    generar_cuotas_para_periodo(periodos[0])
    pago = registrar_pago(
        asociado=asociado_activo,
        fecha=date(2026, 4, 5),
        importe=Decimal("4000"),
        metodo=Pago.METODO_EFECTIVO,
    )
    cuota = Cuota.objects.get(asociado=asociado_activo, periodo=periodos[0])
    assert cuota.importe_pagado == Decimal("4000")
    assert cuota.estado == Cuota.ESTADO_PAGADA


@pytest.mark.django_db
def test_pago_fuera_de_termino_con_donacion(asociado_activo, periodos):
    generar_cuotas_para_periodo(periodos[0])
    pago = registrar_pago(
        asociado=asociado_activo,
        fecha=date(2026, 3, 12),
        importe=Decimal("4000"),
        metodo=Pago.METODO_EFECTIVO,
    )
    cuota = Cuota.objects.get(asociado=asociado_activo, periodo=periodos[0])
    assert cuota.importe_pagado == Decimal("3500")
    assert cuota.estado == Cuota.ESTADO_PAGADA
    assert pago.importe == Decimal("4000")

    donacion = Donacion.objects.get(pago=pago)
    assert donacion.importe == Decimal("500")


@pytest.mark.django_db
def test_asociado_sin_deuda_rechaza_pago(asociado_activo):
    with pytest.raises(ValueError, match="no tiene deuda"):
        registrar_pago(
            asociado=asociado_activo,
            fecha=date(2026, 3, 5),
            importe=Decimal("3000"),
            metodo=Pago.METODO_EFECTIVO,
        )


@pytest.mark.django_db
def test_cuotas_copian_recargos_desde_periodo(asociado_activo, periodos):
    generar_cuotas_para_periodo(periodos[0])
    cuota = Cuota.objects.get(asociado=asociado_activo, periodo=periodos[0])
    assert cuota.importe_recargo_mes == periodos[0].importe_recargo_mes
    assert cuota.importe_recargo_mes_siguiente == periodos[0].importe_recargo_mes_siguiente


@pytest.mark.django_db
def test_generar_cuotas_iniciales_para_asociado_usa_periodos_existentes():
    asociado = create_asociado(
        nombre="Lara",
        apellido="Diaz",
        dni="42123456",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 5, 20),
        fecha_inicio_cobro=date(2026, 4, 1),
    )
    ciclo = CicloLectivo.objects.create(anio=2026)
    abril = PeriodoCuota.objects.create(
        mes=4,
        ciclo_lectivo=ciclo,
        importe=Decimal("3000"),
        importe_recargo_mes=Decimal("500"),
        importe_recargo_mes_siguiente=Decimal("500"),
        fecha_vencimiento=date(2026, 4, 10),
    )
    mayo = PeriodoCuota.objects.create(
        mes=5,
        ciclo_lectivo=ciclo,
        importe=Decimal("3000"),
        importe_recargo_mes=Decimal("500"),
        importe_recargo_mes_siguiente=Decimal("500"),
        fecha_vencimiento=date(2026, 5, 10),
    )

    cuotas = generar_cuotas_iniciales_para_asociado(asociado=asociado, fecha_referencia=date(2026, 5, 20))

    assert [cuota.periodo for cuota in cuotas] == [abril, mayo]
    assert Cuota.objects.filter(asociado=asociado).count() == 2


@pytest.mark.django_db
def test_generar_cuotas_iniciales_no_crea_periodos_faltantes():
    asociado = create_asociado(
        nombre="Nina",
        apellido="Moya",
        dni="43123456",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 5, 20),
        fecha_inicio_cobro=date(2026, 4, 1),
    )
    ciclo = CicloLectivo.objects.create(anio=2026)
    mayo = PeriodoCuota.objects.create(
        mes=5,
        ciclo_lectivo=ciclo,
        importe=Decimal("3000"),
        importe_recargo_mes=Decimal("500"),
        importe_recargo_mes_siguiente=Decimal("500"),
        fecha_vencimiento=date(2026, 5, 10),
    )

    cuotas = generar_cuotas_iniciales_para_asociado(asociado=asociado, fecha_referencia=date(2026, 5, 20))

    assert [cuota.periodo for cuota in cuotas] == [mayo]
    assert PeriodoCuota.objects.filter(mes=4, ciclo_lectivo__anio=2026).exists() is False



@pytest.mark.django_db
def test_no_se_pueden_pagar_cuotas_adelantadas(asociado_activo):
    """No hay cuotas futuras generadas, no se puede pagar por adelantado."""
    with pytest.raises(ValueError, match="no tiene deuda"):
        registrar_pago(
            asociado=asociado_activo,
            fecha=date(2026, 6, 15),
            importe=Decimal("3000"),
            metodo=Pago.METODO_EFECTIVO,
        )
