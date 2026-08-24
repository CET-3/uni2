from datetime import date
from decimal import Decimal

import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from asociados.admin import AsociadoAdmin, AsociadoAdminForm
from asociados.models import Asociado, CicloLectivo, ClasificacionAdherente, Curso
from cuotas.models import Cuota, Donacion, Pago, PagoCuota, PeriodoCuota


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
    assert form.cleaned_data["fecha_inicio_cobro"] == date(2026, 3, 1)


@pytest.mark.django_db
def test_admin_form_calcula_inicio_del_mes_para_adherente():
    clasificacion = ClasificacionAdherente.objects.get(nombre="Familiar")
    form = AsociadoAdminForm(
        data={
            "usuario": "",
            "nombre": "Lia",
            "apellido": "Mora",
            "dni": "40111223",
            "email": "",
            "telefono": "",
            "direccion": "",
            "tipo": Asociado.TIPO_ADHERENTE,
            "curso_actual": "",
            "clasificacion_adherente": clasificacion.pk,
            "estado": Asociado.ESTADO_ACTIVO,
            "fecha_alta": "2026-05-31",
            "fecha_inicio_cobro": "",
            "fecha_baja": "",
            "motivo_baja": "",
        }
    )

    assert form.is_valid(), form.errors
    assert form.cleaned_data["fecha_inicio_cobro"] == date(2026, 5, 1)


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


@pytest.mark.django_db
def test_borrar_curso_deja_al_asociado_sin_curso(curso):
    asociado = Asociado.objects.create(
        nombre="Ana",
        apellido="Perez",
        dni="40111222",
        tipo=Asociado.TIPO_ASOCIADO,
        curso_actual=curso,
        fecha_alta=date(2026, 3, 1),
        fecha_inicio_cobro=date(2026, 3, 1),
    )

    curso.delete()

    asociado.refresh_from_db()
    assert asociado.curso_actual is None


@pytest.mark.django_db
def test_borrar_usuario_deja_al_asociado_sin_usuario():
    usuario = get_user_model().objects.create_user(username="asociado", password="secreto123")
    asociado = Asociado.objects.create(
        usuario=usuario,
        nombre="Ana",
        apellido="Perez",
        dni="40111222",
        tipo=Asociado.TIPO_ADHERENTE,
        fecha_alta=date(2026, 3, 1),
        fecha_inicio_cobro=date(2026, 3, 1),
    )

    usuario.delete()

    asociado.refresh_from_db()
    assert asociado.usuario is None


@pytest.mark.django_db
def test_borrar_asociado_elimina_sus_registros_financieros():
    asociado = Asociado.objects.create(
        nombre="Ana",
        apellido="Perez",
        dni="40111222",
        tipo=Asociado.TIPO_ADHERENTE,
        fecha_alta=date(2026, 3, 1),
        fecha_inicio_cobro=date(2026, 3, 1),
    )
    ciclo_lectivo = CicloLectivo.objects.create(anio=2026)
    periodo = PeriodoCuota.objects.create(
        mes=3,
        ciclo_lectivo=ciclo_lectivo,
        importe=Decimal("1000.00"),
        fecha_vencimiento=date(2026, 3, 10),
    )
    cuota = Cuota.objects.create(asociado=asociado, periodo=periodo, importe=Decimal("1000.00"))
    pago = Pago.objects.create(
        asociado=asociado,
        fecha=date(2026, 3, 5),
        importe=Decimal("1100.00"),
        metodo=Pago.METODO_EFECTIVO,
    )
    PagoCuota.objects.create(pago=pago, cuota=cuota, importe=Decimal("1000.00"))
    Donacion.objects.create(
        asociado=asociado,
        pago=pago,
        importe=Decimal("100.00"),
        fecha=date(2026, 3, 5),
    )
    superusuario = get_user_model().objects.create_superuser(
        username="root_limpieza",
        password="secreto123",
    )
    request = RequestFactory().get("/admin/asociados/asociado/")
    request.user = superusuario
    model_admin = admin.site._registry[Asociado]

    _, _, permisos_necesarios, objetos_protegidos = model_admin.get_deleted_objects(
        [asociado],
        request,
    )

    assert permisos_necesarios == set()
    assert objetos_protegidos == []
    asociado.delete()

    assert not Cuota.objects.exists()
    assert not Pago.objects.exists()
    assert not PagoCuota.objects.exists()
    assert not Donacion.objects.exists()
