from datetime import date

import pytest

from asociados.models import Asociado, ClasificacionAdherente
from asociados.selectors import filter_asociados


@pytest.mark.django_db
def test_filtra_adherentes_por_clasificacion():
    docente = ClasificacionAdherente.objects.get(nombre="Docente")
    familiar = ClasificacionAdherente.objects.get(nombre="Familiar")
    esperado = Asociado.objects.create(
        nombre="Ana", apellido="Pérez", dni="40111222", tipo="adherente",
        clasificacion_adherente=docente, fecha_alta=date(2026, 8, 1), fecha_inicio_cobro=date(2026, 8, 1),
    )
    Asociado.objects.create(
        nombre="Lía", apellido="Mora", dni="40111223", tipo="adherente",
        clasificacion_adherente=familiar, fecha_alta=date(2026, 8, 1), fecha_inicio_cobro=date(2026, 8, 1),
    )

    assert list(filter_asociados(clasificacion_adherente_id=docente.pk)) == [esperado]
