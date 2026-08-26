from types import SimpleNamespace

import pytest
from django.contrib.auth import get_user_model

from auditoria.models import EventoAuditoria
from auditoria.templatetags.auditoria import (
    actor_evento_auditoria,
    objeto_evento_auditoria,
    valor_campo_auditoria,
    verbo_evento_auditoria,
)


@pytest.mark.django_db
def test_presentacion_usa_nombre_actual_en_evento_historico_con_username():
    actor = get_user_model().objects.create_user(
        username="49002269",
        first_name="Candela",
        last_name="Narvaja",
    )
    evento = EventoAuditoria.objects.create(
        actor=actor,
        actor_etiqueta="49002269",
        accion=EventoAuditoria.ACCION_MODIFICAR,
        entidad="cuotas.Cuota",
        objeto_id="1",
        objeto_descripcion="Altamirano, Iván - 05/2026",
        cambios={},
        origen=EventoAuditoria.ORIGEN_GESTION,
    )

    assert actor_evento_auditoria(evento) == "Candela Narvaja"


def test_presentacion_humaniza_aplicacion_de_pago():
    evento = SimpleNamespace(
        entidad="cuotas.PagoCuota",
        accion="crear",
        cambios={
            "cuota": {
                "nuevo": {"id": 1, "texto": "Altamirano, Iván Emanuel - 05/2026"}
            },
            "importe": {"nuevo": "1000.00"},
        },
    )

    assert verbo_evento_auditoria(evento) == "aplicó"
    assert objeto_evento_auditoria(evento) == (
        "$ 1.000,00 a la cuota 05/2026 de Altamirano, Iván Emanuel"
    )


def test_objeto_de_auditoria_incluye_tipo_y_descripcion():
    evento = SimpleNamespace(
        entidad="asociados.Asociado",
        accion="modificar",
        objeto_descripcion="Campos, Julia",
        cambios={},
    )

    assert objeto_evento_auditoria(evento) == "el asociado Campos, Julia"


def test_valores_financieros_de_auditoria_se_muestran_legibles():
    assert valor_campo_auditoria("1000.00", "importe", "cuotas.Pago") == "$ 1.000,00"
    assert valor_campo_auditoria("efectivo", "metodo", "cuotas.Pago") == "Efectivo"
    assert valor_campo_auditoria("2026-08-09", "fecha", "cuotas.Pago") == "09/08/2026"
