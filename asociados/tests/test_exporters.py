from datetime import date
from io import BytesIO

import pytest
from openpyxl import load_workbook

from asociados.exporters import build_asociados_formato_uni2_xlsx
from asociados.models import Asociado, ClasificacionAdherente


@pytest.mark.django_db
def test_exporta_clasificacion_del_adherente():
    docente = ClasificacionAdherente.objects.get(nombre="Docente")
    adherente = Asociado.objects.create(
        nombre="Ana", apellido="Pérez", dni="40111222", tipo="adherente",
        clasificacion_adherente=docente, fecha_alta=date(2026, 8, 1), fecha_inicio_cobro=date(2026, 8, 1),
    )

    workbook = load_workbook(BytesIO(build_asociados_formato_uni2_xlsx([adherente])))
    rows = list(workbook["ASOCIADOS"].values)

    indice = rows[0].index("clasificacion_adherente")
    assert rows[1][indice] == "Docente"
