import pytest
from django.core.exceptions import ValidationError

from contenidos.models import Beneficio
from contenidos.selectors import get_beneficios_publicos


@pytest.mark.django_db
def test_get_beneficios_publicos_solo_activos():
    Beneficio.objects.create(titulo="Activo", descripcion="Visible", activo=True, orden=1)
    Beneficio.objects.create(titulo="Inactivo", descripcion="Oculto", activo=False, orden=2)

    resultado = list(get_beneficios_publicos())

    assert len(resultado) == 1
    assert resultado[0].titulo == "Activo"


@pytest.mark.django_db
def test_get_beneficios_publicos_ordenados_por_orden():
    Beneficio.objects.create(titulo="Tercero", descripcion="Tercero", activo=True, orden=3)
    Beneficio.objects.create(titulo="Primero", descripcion="Primero", activo=True, orden=1)
    Beneficio.objects.create(titulo="Segundo", descripcion="Segundo", activo=True, orden=2)

    resultado = list(get_beneficios_publicos())

    assert [b.titulo for b in resultado] == ["Primero", "Segundo", "Tercero"]


def test_beneficio_usa_rotulos_con_tilde():
    assert Beneficio._meta.get_field("titulo").verbose_name == "título"
    assert Beneficio._meta.get_field("descripcion").verbose_name == "descripción"


def test_beneficio_documenta_campos_para_admin():
    assert Beneficio._meta.get_field("titulo").help_text == "Nombre visible del beneficio."
    assert Beneficio._meta.get_field("descripcion").help_text == "Texto público que explica el beneficio."
    assert Beneficio._meta.get_field("activo").help_text == "Indica si el beneficio se publica en el sitio."
    assert Beneficio._meta.get_field("orden").help_text == "Posición usada para ordenar los beneficios publicados."


@pytest.mark.django_db
def test_beneficio_requiere_titulo_y_descripcion():
    beneficio = Beneficio(titulo="", descripcion="")

    with pytest.raises(ValidationError):
        beneficio.full_clean()
