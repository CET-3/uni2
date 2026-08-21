from datetime import date
from decimal import Decimal

import pytest
import cuotas.services as cuotas_services
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.utils import timezone

from asociados.models import Asociado, CicloLectivo, ClasificacionAdherente, Curso
from asociados.services import create_asociado
from cuotas.models import Cuota, Donacion, Pago, PeriodoCuota
from cuotas.services import (
    crear_periodo_cuota,
    generar_cuotas_iniciales_para_asociado,
    generar_cuotas_para_periodo,
    registrar_donacion,
    registrar_pago,
)


def test_cuotas_iniciales_bloquean_periodos_para_coordinar_generacion_masiva():
    obtener_periodos = getattr(cuotas_services, "_get_periodos_activos_para_alta", None)

    assert obtener_periodos is not None
    queryset = obtener_periodos()
    assert queryset.query.select_for_update is True


@pytest.mark.django_db
def test_crear_periodo_rechaza_vencimiento_fuera_del_mismo_mes():
    ciclo = CicloLectivo.objects.create(anio=2026)

    with pytest.raises(ValidationError, match="dentro del período seleccionado"):
        crear_periodo_cuota(
            datos={
                "mes": 8,
                "ciclo_lectivo": ciclo,
                "importe": Decimal("3000.00"),
                "importe_recargo_mes": Decimal("500.00"),
                "importe_recargo_mes_siguiente": Decimal("500.00"),
                "fecha_vencimiento": date(2026, 9, 1),
                "activo": True,
            },
            actor=None,
        )

    assert PeriodoCuota.objects.count() == 0


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
def test_periodo_nuevo_comienza_sin_generacion_registrada(periodos):
    assert periodos[0].generado_el is None


@pytest.mark.django_db
def test_generacion_marca_el_periodo_aunque_no_cree_cuotas():
    ciclo = CicloLectivo.objects.create(anio=2026)
    periodo = PeriodoCuota.objects.create(
        mes=8,
        ciclo_lectivo=ciclo,
        importe=Decimal("3000"),
        fecha_vencimiento=date(2026, 8, 10),
    )
    momento_anterior = timezone.now()

    creadas = generar_cuotas_para_periodo(periodo)

    periodo.refresh_from_db()
    assert creadas == 0
    assert periodo.generado_el is not None
    assert periodo.generado_el >= momento_anterior


@pytest.mark.django_db
def test_reintentar_generacion_conserva_la_primera_fecha(periodos):
    periodo = periodos[0]
    generar_cuotas_para_periodo(periodo)
    periodo.refresh_from_db()
    primera_generacion = periodo.generado_el

    generar_cuotas_para_periodo(periodo)

    periodo.refresh_from_db()
    assert periodo.generado_el == primera_generacion


@pytest.mark.django_db
def test_no_generar_cuotas_duplicadas(asociado_activo, periodos):
    generar_cuotas_para_periodo(periodos[0])
    creadas = generar_cuotas_para_periodo(periodos[0])
    assert creadas == 0


@pytest.mark.django_db
def test_periodo_con_cuotas_no_se_puede_borrar(asociado_activo, periodos):
    periodo = periodos[0]
    generar_cuotas_para_periodo(periodo)
    cuota = Cuota.objects.get(asociado=asociado_activo, periodo=periodo)

    with pytest.raises(ProtectedError):
        periodo.delete()

    assert PeriodoCuota.objects.filter(pk=periodo.pk).exists()
    assert Cuota.objects.filter(pk=cuota.pk).exists()


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
        fecha_inicio_cobro=date(2026, 4, 1),
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
def test_asociado_sin_deuda_puede_registrar_una_donacion(asociado_activo):
    pago = registrar_donacion(
        asociado=asociado_activo,
        fecha=date(2026, 3, 5),
        importe=Decimal("3000"),
        metodo=Pago.METODO_EFECTIVO,
        observaciones="Aporte voluntario",
    )

    assert pago.importe == Decimal("3000")
    assert not pago.aplicaciones.exists()
    donacion = Donacion.objects.get(pago=pago)
    assert donacion.asociado == asociado_activo
    assert donacion.importe == Decimal("3000")
    assert donacion.observaciones == "Aporte voluntario"


@pytest.mark.django_db
def test_no_permite_registrar_donacion_si_hay_cuotas_pendientes(asociado_activo, periodos):
    generar_cuotas_para_periodo(periodos[0])

    with pytest.raises(ValueError, match="tiene cuotas pendientes"):
        registrar_donacion(
            asociado=asociado_activo,
            fecha=date(2026, 3, 5),
            importe=Decimal("3000"),
            metodo=Pago.METODO_EFECTIVO,
        )

    assert not Pago.objects.exists()


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
def test_cuotas_iniciales_dependen_del_tipo_del_alta():
    ciclo = CicloLectivo.objects.create(anio=2026)
    periodos = [
        PeriodoCuota.objects.create(
            mes=mes,
            ciclo_lectivo=ciclo,
            importe=Decimal("3000"),
            fecha_vencimiento=date(2026, mes, 10),
        )
        for mes in (3, 4, 5)
    ]
    asociado = create_asociado(
        nombre="Ana",
        apellido="Paz",
        dni="43123457",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 5, 31),
    )
    adherente = create_asociado(
        nombre="Luz",
        apellido="Paz",
        dni="43123458",
        tipo=Asociado.TIPO_ADHERENTE,
        fecha_alta=date(2026, 5, 31),
        clasificacion_adherente=ClasificacionAdherente.objects.get(nombre="Familiar"),
    )

    cuotas_asociado = generar_cuotas_iniciales_para_asociado(
        asociado=asociado,
        fecha_referencia=date(2026, 5, 31),
    )
    cuotas_adherente = generar_cuotas_iniciales_para_asociado(
        asociado=adherente,
        fecha_referencia=date(2026, 5, 31),
    )

    assert [cuota.periodo for cuota in cuotas_asociado] == periodos
    assert [cuota.periodo for cuota in cuotas_adherente] == [periodos[-1]]


@pytest.mark.django_db
def test_cuotas_iniciales_incluyen_solo_futuros_que_ya_fueron_generados():
    ciclo = CicloLectivo.objects.create(anio=2026)
    mayo = PeriodoCuota.objects.create(
        mes=5,
        ciclo_lectivo=ciclo,
        importe=Decimal("3000"),
        fecha_vencimiento=date(2026, 5, 10),
    )
    junio = PeriodoCuota.objects.create(
        mes=6,
        ciclo_lectivo=ciclo,
        importe=Decimal("3100"),
        fecha_vencimiento=date(2026, 6, 10),
    )
    julio = PeriodoCuota.objects.create(
        mes=7,
        ciclo_lectivo=ciclo,
        importe=Decimal("3200"),
        fecha_vencimiento=date(2026, 7, 10),
    )
    agosto = PeriodoCuota.objects.create(
        mes=8,
        ciclo_lectivo=ciclo,
        importe=Decimal("3300"),
        fecha_vencimiento=date(2026, 8, 10),
    )
    generar_cuotas_para_periodo(junio)
    generar_cuotas_para_periodo(agosto)
    asociado = create_asociado(
        nombre="Leo",
        apellido="Sur",
        dni="43123459",
        tipo=Asociado.TIPO_ADHERENTE,
        fecha_alta=date(2026, 5, 31),
    )

    cuotas = generar_cuotas_iniciales_para_asociado(
        asociado=asociado,
        fecha_referencia=date(2026, 5, 31),
    )

    assert [cuota.periodo for cuota in cuotas] == [mayo, junio, agosto]
    assert not Cuota.objects.filter(asociado=asociado, periodo=julio).exists()


@pytest.mark.django_db
def test_cuotas_iniciales_ignoran_periodos_inactivos_y_cruzan_el_anio():
    ciclo_2025 = CicloLectivo.objects.create(anio=2025)
    ciclo_2026 = CicloLectivo.objects.create(anio=2026)
    noviembre = PeriodoCuota.objects.create(
        mes=11,
        ciclo_lectivo=ciclo_2025,
        importe=Decimal("3000"),
        fecha_vencimiento=date(2025, 11, 10),
    )
    PeriodoCuota.objects.create(
        mes=12,
        ciclo_lectivo=ciclo_2025,
        importe=Decimal("3000"),
        fecha_vencimiento=date(2025, 12, 10),
        activo=False,
    )
    enero = PeriodoCuota.objects.create(
        mes=1,
        ciclo_lectivo=ciclo_2026,
        importe=Decimal("3000"),
        fecha_vencimiento=date(2026, 1, 10),
    )
    asociado = create_asociado(
        nombre="Noa",
        apellido="Sur",
        dni="43123460",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 1, 31),
    )

    cuotas = generar_cuotas_iniciales_para_asociado(
        asociado=asociado,
        fecha_referencia=date(2026, 1, 31),
    )

    assert [cuota.periodo for cuota in cuotas] == [noviembre, enero]


@pytest.mark.django_db
def test_reintentar_cuotas_iniciales_devuelve_solo_las_nuevas():
    asociado = create_asociado(
        nombre="Uma",
        apellido="Sol",
        dni="43123461",
        tipo=Asociado.TIPO_ADHERENTE,
        fecha_alta=date(2026, 5, 20),
    )
    ciclo = CicloLectivo.objects.create(anio=2026)
    PeriodoCuota.objects.create(
        mes=5,
        ciclo_lectivo=ciclo,
        importe=Decimal("3000"),
        fecha_vencimiento=date(2026, 5, 10),
    )

    primera = generar_cuotas_iniciales_para_asociado(
        asociado=asociado,
        fecha_referencia=date(2026, 5, 20),
    )
    segunda = generar_cuotas_iniciales_para_asociado(
        asociado=asociado,
        fecha_referencia=date(2026, 5, 20),
    )

    assert len(primera) == 1
    assert segunda == []



@pytest.mark.django_db
def test_no_se_pueden_pagar_cuotas_adelantadas(asociado_activo):
    ciclo = CicloLectivo.objects.create(anio=2026)
    futuro = PeriodoCuota.objects.create(
        mes=9,
        ciclo_lectivo=ciclo,
        importe=Decimal("3000"),
        fecha_vencimiento=date(2026, 9, 10),
    )
    Cuota.objects.create(
        asociado=asociado_activo,
        periodo=futuro,
        importe=futuro.importe,
    )

    with pytest.raises(ValueError, match="no tiene deuda"):
        registrar_pago(
            asociado=asociado_activo,
            fecha=date(2026, 8, 20),
            importe=Decimal("3000"),
            metodo=Pago.METODO_EFECTIVO,
        )
