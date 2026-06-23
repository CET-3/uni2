import logging
from datetime import date

import pytest

from asociados.importers import PadronPreview, import_padron_preview
from asociados.models import Asociado
from usuarios.services import ensure_default_groups


def _padron_row(fila_origen, dni, apellido="Leyes", nombre="Lena"):
    return {
        "fila_origen": fila_origen,
        "apellido": apellido,
        "nombre": nombre,
        "dni": dni,
        "tipo": Asociado.TIPO_ADHERENTE,
        "curso": "",
        "curso_anio": "",
        "curso_division": "",
        "division": "",
        "turno": "",
        "telefono": "",
        "email": "",
        "direccion": "",
    }


@pytest.mark.django_db
def test_import_padron_preview_loguea_avance_y_resumen(caplog):
    ensure_default_groups()
    preview = PadronPreview(
        importables=[
            _padron_row(2, "52328996"),
            _padron_row(3, "52536191", apellido="Darosa", nombre="Joaquin"),
        ],
        revisar=[{"fila_origen": 4}],
        no_importar_count=1,
    )

    caplog.set_level(logging.INFO, logger="asociados.importers")

    import_padron_preview(preview, date(2026, 6, 23))

    mensajes = [record.getMessage() for record in caplog.records]
    assert "Importacion de padron inicial iniciada: 2 filas importables." in mensajes
    assert "Importacion de padron inicial: 2/2 filas procesadas." in mensajes
    assert (
        "Importacion de padron inicial finalizada: 2 creados, 0 actualizados, "
        "0 cursos creados, 2 omitidos, 0 errores."
    ) in mensajes
