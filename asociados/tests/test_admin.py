from datetime import date

import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory

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


@pytest.mark.django_db
def test_admin_operativo_no_expone_campos_de_baja():
    operador = get_user_model().objects.create_user(
        username="mutual", password="secreto123", is_staff=True
    )
    request = RequestFactory().get("/admin/asociados/asociado/1/change/")
    request.user = operador
    model_admin = AsociadoAdmin(Asociado, admin.site)

    fields = {
        field
        for _, options in model_admin.get_fieldsets(request)
        for field in options["fields"]
    }

    assert "estado" not in fields
    assert "fecha_baja" not in fields
    assert "motivo_baja" not in fields
