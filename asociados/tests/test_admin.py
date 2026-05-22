from datetime import date

import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from asociados.admin import AsociadoAdmin, AsociadoAdminForm
from asociados.models import Asociado, Colegio, Curso


@pytest.fixture
def curso():
    colegio = Colegio.objects.create(nombre="CET 3")
    return Curso.objects.create(colegio=colegio, nombre="1° 1°")


@pytest.fixture
def admin_user():
    user_model = get_user_model()
    return user_model.objects.create_superuser(
        username="admin_test",
        email="admin_test@example.com",
        password="secreto123",
    )


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
            "fecha_nacimiento": "",
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


@pytest.mark.django_db
def test_admin_save_model_crea_inscripcion_inicial(curso, admin_user):
    site = AdminSite()
    model_admin = AsociadoAdmin(Asociado, site)
    request = RequestFactory().post("/admin/asociados/asociado/add/")
    request.user = admin_user

    asociado = Asociado(
        nombre="Lia",
        apellido="Suarez",
        dni="40111333",
        tipo=Asociado.TIPO_ASOCIADO,
        curso_actual=curso,
        estado=Asociado.ESTADO_ACTIVO,
        fecha_alta=date(2026, 3, 10),
        fecha_inicio_cobro=date(2026, 3, 1),
    )
    form = AsociadoAdminForm(
        data={
            "usuario": "",
            "nombre": "Lia",
            "apellido": "Suarez",
            "dni": "40111333",
            "email": "",
            "telefono": "",
            "fecha_nacimiento": "",
            "tipo": Asociado.TIPO_ASOCIADO,
            "curso_actual": curso.pk,
            "estado": Asociado.ESTADO_ACTIVO,
            "fecha_alta": "2026-03-10",
            "fecha_inicio_cobro": "2026-03-01",
            "fecha_baja": "",
            "motivo_baja": "",
        },
        instance=asociado,
    )
    assert form.is_valid(), form.errors

    model_admin.save_model(request, asociado, form, change=False)

    asociado.refresh_from_db()
    assert asociado.inscripciones.count() == 1
    inscripcion = asociado.inscripciones.get()
    assert inscripcion.curso == curso
    assert inscripcion.ciclo_lectivo == 2026
