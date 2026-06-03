import pytest

from contenidos.models import Beneficio
from contenidos.selectors import get_beneficios_publicos


@pytest.mark.django_db
def test_get_beneficios_publicos_solo_activos():
    Beneficio.objects.create(titulo="Activo", descripcion="", activo=True, orden=1)
    Beneficio.objects.create(titulo="Inactivo", descripcion="", activo=False, orden=2)

    resultado = list(get_beneficios_publicos())

    assert len(resultado) == 1
    assert resultado[0].titulo == "Activo"


@pytest.mark.django_db
def test_get_beneficios_publicos_ordenados_por_orden():
    Beneficio.objects.create(titulo="Tercero", descripcion="", activo=True, orden=3)
    Beneficio.objects.create(titulo="Primero", descripcion="", activo=True, orden=1)
    Beneficio.objects.create(titulo="Segundo", descripcion="", activo=True, orden=2)

    resultado = list(get_beneficios_publicos())

    assert [b.titulo for b in resultado] == ["Primero", "Segundo", "Tercero"]
