import uuid

import pytest
from django.contrib.auth import get_user_model

from auditoria.models import EventoAuditoria
from auditoria.selectors import (
    buscar_operaciones,
    buscar_operaciones_asociado,
    obtener_operaciones,
    obtener_operaciones_asociado,
)


def crear_evento(*, operacion_id, objeto_id, descripcion):
    return EventoAuditoria.objects.create(
        actor_etiqueta="Proceso de prueba",
        accion=EventoAuditoria.ACCION_CREAR,
        entidad="asociados.Asociado",
        objeto_id=objeto_id,
        objeto_descripcion=descripcion,
        cambios={"nombre": {"anterior": None, "nuevo": descripcion}},
        origen=EventoAuditoria.ORIGEN_SISTEMA,
        operacion_id=operacion_id,
    )


@pytest.mark.django_db
def test_buscar_operaciones_devuelve_una_fila_por_operacion():
    operacion_compuesta = uuid.uuid4()
    crear_evento(operacion_id=operacion_compuesta, objeto_id="1", descripcion="Primer evento")
    crear_evento(operacion_id=operacion_compuesta, objeto_id="2", descripcion="Segundo evento")
    crear_evento(operacion_id=uuid.uuid4(), objeto_id="3", descripcion="Evento independiente")

    operaciones = list(buscar_operaciones())

    assert len(operaciones) == 2
    assert {operacion["operacion_id"] for operacion in operaciones} == {
        operacion_compuesta,
        EventoAuditoria.objects.get(objeto_id="3").operacion_id,
    }


@pytest.mark.django_db
def test_obtener_operaciones_recupera_todos_los_eventos_aunque_el_filtro_coincida_con_uno():
    operacion_id = uuid.uuid4()
    crear_evento(operacion_id=operacion_id, objeto_id="10", descripcion="Coincide")
    crear_evento(operacion_id=operacion_id, objeto_id="11", descripcion="Relacionado")

    resumenes = list(buscar_operaciones(objeto_id="10"))
    operaciones = obtener_operaciones(resumenes)

    assert len(operaciones) == 1
    assert operaciones[0].es_compuesta
    assert {evento.objeto_id for evento in operaciones[0].eventos} == {"10", "11"}


@pytest.mark.django_db
def test_operacion_usa_un_titulo_de_negocio_para_un_cobro():
    operacion_id = uuid.uuid4()
    evento_pago = EventoAuditoria.objects.create(
        actor_etiqueta="Proceso de prueba",
        accion=EventoAuditoria.ACCION_CREAR,
        entidad="cuotas.Pago",
        objeto_id="40",
        objeto_descripcion="Pago 40",
        cambios={},
        origen=EventoAuditoria.ORIGEN_SISTEMA,
        operacion_id=operacion_id,
    )
    evento_relacionado = crear_evento(
        operacion_id=operacion_id,
        objeto_id="41",
        descripcion="Cuota relacionada",
    )

    operacion = obtener_operaciones([{"operacion_id": operacion_id}])[0]

    assert {evento.id for evento in operacion.eventos} == {
        evento_pago.id,
        evento_relacionado.id,
    }
    assert operacion.titulo == "Cobro de cuotas"


@pytest.mark.django_db
def test_busqueda_encuentra_el_nombre_de_usuario_actual():
    actor = get_user_model().objects.create_user(username="operadora_actual")
    EventoAuditoria.objects.create(
        actor=actor,
        actor_etiqueta="Nombre histórico",
        accion=EventoAuditoria.ACCION_MODIFICAR,
        entidad="asociados.Asociado",
        objeto_id="50",
        objeto_descripcion="Campos, Julia",
        cambios={},
        origen=EventoAuditoria.ORIGEN_GESTION,
    )

    operaciones = list(buscar_operaciones(actor_query="operadora_actual"))

    assert len(operaciones) == 1


@pytest.mark.django_db
def test_busqueda_de_objeto_no_se_mezcla_con_la_busqueda_del_actor():
    operacion_id = uuid.uuid4()
    crear_evento(
        operacion_id=operacion_id,
        objeto_id="60",
        descripcion="Objeto buscado",
    )

    assert list(buscar_operaciones(objeto_query="Objeto buscado"))
    assert not list(buscar_operaciones(actor_query="Objeto buscado"))


@pytest.mark.django_db
def test_operaciones_asociado_incluyen_pago_y_eventos_de_la_misma_operacion():
    operacion_id = uuid.uuid4()
    evento_pago = EventoAuditoria.objects.create(
        actor_etiqueta="Proceso de prueba",
        accion=EventoAuditoria.ACCION_CREAR,
        entidad="cuotas.Pago",
        objeto_id="80",
        objeto_descripcion="Pago 80",
        cambios={
            "asociado": {
                "anterior": None,
                "nuevo": {"id": 12, "texto": "Campos, Julia"},
            }
        },
        origen=EventoAuditoria.ORIGEN_GESTION,
        operacion_id=operacion_id,
    )
    evento_imputacion = EventoAuditoria.objects.create(
        actor_etiqueta="Proceso de prueba",
        accion=EventoAuditoria.ACCION_CREAR,
        entidad="cuotas.PagoCuota",
        objeto_id="81",
        objeto_descripcion="Imputación 81",
        cambios={},
        origen=EventoAuditoria.ORIGEN_GESTION,
        operacion_id=operacion_id,
    )

    resumenes = buscar_operaciones_asociado(12)
    operaciones = obtener_operaciones_asociado(resumenes, 12)

    assert len(operaciones) == 1
    assert operaciones[0].titulo == "Cobro de cuotas"
    assert {evento.id for evento in operaciones[0].eventos} == {
        evento_pago.id,
        evento_imputacion.id,
    }


@pytest.mark.django_db
def test_operacion_masiva_no_expone_eventos_de_otro_asociado():
    operacion_id = uuid.uuid4()
    eventos = []
    for asociado_id, nombre in ((12, "Campos, Julia"), (13, "Rivas, Mora")):
        eventos.append(
            EventoAuditoria.objects.create(
                actor_etiqueta="Proceso de prueba",
                accion=EventoAuditoria.ACCION_CREAR,
                entidad="cuotas.Cuota",
                objeto_id=str(100 + asociado_id),
                objeto_descripcion=f"Cuota de {nombre}",
                cambios={
                    "asociado": {
                        "anterior": None,
                        "nuevo": {"id": asociado_id, "texto": nombre},
                    }
                },
                origen=EventoAuditoria.ORIGEN_SISTEMA,
                operacion_id=operacion_id,
            )
        )

    operaciones = obtener_operaciones_asociado(
        buscar_operaciones_asociado(12),
        12,
    )

    assert len(operaciones) == 1
    assert operaciones[0].eventos == (eventos[0],)
