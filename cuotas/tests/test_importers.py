import logging
from datetime import date

import pytest

from asociados.models import Asociado
from asociados.services import create_asociado
from cuotas.importers import CuotasHistoricasPreview, import_cuotas_historicas_preview
from cuotas.models import Pago


@pytest.mark.django_db
def test_import_cuotas_historicas_preview_loguea_avance_y_resumen(caplog):
    asociado = create_asociado(
        nombre="Lena",
        apellido="Leyes",
        dni="52328996",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 3, 1),
    )
    preview = CuotasHistoricasPreview(
        importables=[
            {
                "fila_origen": 8,
                "mes": 3,
                "mes_nombre": "Mar",
                "pagada": True,
                "metodo": Pago.METODO_EFECTIVO,
                "asociado_id": asociado.id,
                "estado": "pagada",
            },
            {
                "fila_origen": 8,
                "mes": 4,
                "mes_nombre": "Abr",
                "pagada": False,
                "metodo": "",
                "asociado_id": asociado.id,
                "estado": "vencida",
            },
        ],
        revisar=[{"fila_origen": 9}],
        omitidas=1,
    )

    caplog.set_level(logging.INFO, logger="cuotas.importers")

    import_cuotas_historicas_preview(preview)

    mensajes = [record.getMessage() for record in caplog.records]
    assert "Importacion de cuotas historicas iniciada: 2 cuotas importables." in mensajes
    assert "Importacion de cuotas historicas: 2/2 cuotas procesadas." in mensajes
    assert (
        "Importacion de cuotas historicas finalizada: 2 periodos creados, 2 cuotas creadas, "
        "1 pagos creados, 1 omitidas, 0 errores."
    ) in mensajes
