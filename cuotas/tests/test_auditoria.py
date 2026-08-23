from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from asociados.models import Asociado, CicloLectivo
from asociados.services import create_asociado
from auditoria.models import EventoAuditoria
from cuotas.models import Cuota, Pago, PeriodoCuota
from cuotas.services import generar_cuotas_para_periodo, registrar_pago


@pytest.fixture
def escenario_cobro():
    asociado = create_asociado(
        nombre="Ludmila",
        apellido="Aillal",
        dni="40111777",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 3, 1),
    )
    ciclo = CicloLectivo.objects.create(anio=2026)
    periodo = PeriodoCuota.objects.create(
        mes=3,
        ciclo_lectivo=ciclo,
        importe=Decimal("3000"),
        importe_recargo_mes=Decimal("500"),
        importe_recargo_mes_siguiente=Decimal("500"),
        fecha_vencimiento=date(2026, 3, 10),
    )
    return asociado, periodo


@pytest.mark.django_db
def test_cobro_agrupa_todos_sus_eventos(escenario_cobro):
    asociado, periodo = escenario_cobro
    actor = get_user_model().objects.create_user(username="cajera", password="secreto123")
    generar_cuotas_para_periodo(periodo, actor=actor)
    ultimo_evento_id = EventoAuditoria.objects.order_by("-id").values_list("id", flat=True).first() or 0

    pago = registrar_pago(
        asociado=asociado,
        fecha=date(2026, 3, 5),
        importe=Decimal("3500"),
        metodo=Pago.METODO_EFECTIVO,
        registrado_por=actor,
    )

    eventos = list(EventoAuditoria.objects.filter(id__gt=ultimo_evento_id).order_by("id"))
    assert {evento.entidad for evento in eventos} == {
        "cuotas.Pago",
        "cuotas.PagoCuota",
        "cuotas.Cuota",
        "cuotas.Donacion",
    }
    assert len({evento.operacion_id for evento in eventos}) == 1
    assert all(evento.actor == actor for evento in eventos)
    assert next(evento for evento in eventos if evento.entidad == "cuotas.Pago").objeto_id == str(pago.pk)


@pytest.mark.django_db
def test_generacion_de_cuotas_registra_actor_y_operacion(escenario_cobro):
    _, periodo = escenario_cobro
    actor = get_user_model().objects.create_user(username="tesorera", password="secreto123")

    creadas = generar_cuotas_para_periodo(periodo, actor=actor)

    eventos = EventoAuditoria.objects.filter(entidad="cuotas.Cuota")
    assert creadas == 1
    assert eventos.count() == Cuota.objects.filter(periodo=periodo).count()
    assert set(eventos.values_list("actor", flat=True)) == {actor.pk}


@pytest.mark.django_db
def test_reintentar_generacion_no_repite_evento_del_periodo(escenario_cobro):
    _, periodo = escenario_cobro

    generar_cuotas_para_periodo(periodo)
    generar_cuotas_para_periodo(periodo)

    eventos = EventoAuditoria.objects.filter(
        entidad="cuotas.PeriodoCuota",
        accion=EventoAuditoria.ACCION_MODIFICAR,
        objeto_id=str(periodo.pk),
    )
    assert eventos.count() == 1
    assert set(eventos.get().cambios) == {"generado_el"}
