from datetime import date

import pytest

from asociados.admin import AsociadoAdmin, AsociadoAdminForm
from asociados.models import Asociado, Curso


@pytest.fixture
def curso():
    return Curso.objects.create(anio="1ro", curso="1ra", division=Curso.DIVISION_CB, turno=Curso.TURNO_TM)


@pytest.mark.django_db
def test_admin_form_calcula_fecha_inicio_cobro(curso):
    form = AsociadoAdminForm(
        data={
            "usuario": "",
            "nombre": "Ana",
            "apellido": "Perez",
            "dni": "40111222",
            "email": "",
            "telefono": "",
            "direccion": "",
            "tipo": Asociado.TIPO_ASOCIADO,
            "curso_actual": curso.pk,
            "estado": Asociado.ESTADO_ACTIVO,
            "fecha_alta": "2026-05-20",
            "fecha_inicio_cobro": "",
            "fecha_baja": "",
            "motivo_baja": "",
        }
    )

    assert form.is_valid(), form.errors
    assert form.cleaned_data["fecha_inicio_cobro"] == date(2026, 6, 1)


def test_asociado_admin_usa_autocomplete_para_usuario():
    assert AsociadoAdmin.autocomplete_fields == ("usuario",)
