from datetime import date

import pytest

from asociados.models import Asociado, CicloLectivo, ClasificacionAdherente, Curso
from gestion.forms import AsociadoAltaForm, AsociadoGestionForm, PeriodoCuotaForm


@pytest.fixture
def curso():
    return Curso.objects.create(
        anio="1ro",
        curso="1ra",
        division=Curso.DIVISION_CB,
        turno=Curso.TURNO_TM,
    )


def datos_base(**overrides):
    data = {
        "nombre": "Ana",
        "apellido": "Pérez",
        "dni": "40111222",
        "email": "",
        "telefono": "",
        "direccion": "",
        "tipo": Asociado.TIPO_ADHERENTE,
        "curso_actual": "",
        "clasificacion_adherente": "",
        "fecha_alta": "2026-08-01",
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
@pytest.mark.parametrize("fecha_vencimiento", ["2026-07-31", "2026-09-01"])
def test_periodo_rechaza_vencimiento_fuera_del_mismo_mes(fecha_vencimiento):
    ciclo = CicloLectivo.objects.create(anio=2026)
    form = PeriodoCuotaForm(
        data={
            "mes": 8,
            "ciclo_lectivo": ciclo.pk,
            "importe": "3000.00",
            "importe_recargo_mes": "500.00",
            "importe_recargo_mes_siguiente": "500.00",
            "fecha_vencimiento": fecha_vencimiento,
            "activo": "on",
        }
    )

    assert form.is_valid() is False
    assert form.errors["fecha_vencimiento"] == [
        "La fecha de vencimiento debe estar dentro del período seleccionado."
    ]


@pytest.mark.django_db
@pytest.mark.parametrize("fecha_vencimiento", ["2026-08-01", "2026-08-31"])
def test_periodo_acepta_vencimiento_dentro_del_mismo_mes(fecha_vencimiento):
    ciclo = CicloLectivo.objects.create(anio=2026)
    form = PeriodoCuotaForm(
        data={
            "mes": 8,
            "ciclo_lectivo": ciclo.pk,
            "importe": "3000.00",
            "importe_recargo_mes": "500.00",
            "importe_recargo_mes_siguiente": "500.00",
            "fecha_vencimiento": fecha_vencimiento,
            "activo": "on",
        }
    )

    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_alta_no_ofrece_sin_clasificar():
    form = AsociadoAltaForm()

    nombres = list(form.fields["clasificacion_adherente"].queryset.values_list("nombre", flat=True))

    assert "Docente" in nombres
    assert "Sin clasificar" not in nombres


@pytest.mark.django_db
def test_alta_operativa_no_expone_fechas_administrativas():
    form = AsociadoAltaForm()

    assert "fecha_alta" not in form.fields
    assert "fecha_inicio_cobro" not in form.fields


@pytest.mark.django_db
def test_alta_adherente_requiere_clasificacion():
    form = AsociadoAltaForm(data=datos_base())

    assert form.is_valid() is False
    assert form.errors["clasificacion_adherente"] == ["Elegí una clasificación para el adherente."]


@pytest.mark.django_db
def test_alta_asociado_conserva_curso_y_limpia_clasificacion(curso):
    clasificacion = ClasificacionAdherente.objects.get(nombre="Docente")
    form = AsociadoAltaForm(
        data=datos_base(
            tipo=Asociado.TIPO_ASOCIADO,
            curso_actual=curso.pk,
            clasificacion_adherente=clasificacion.pk,
        )
    )

    assert form.is_valid(), form.errors
    assert form.cleaned_data["curso_actual"] == curso
    assert form.cleaned_data["clasificacion_adherente"] is None


@pytest.mark.django_db
def test_edicion_adherente_conserva_clasificacion_y_limpia_curso(curso):
    clasificacion = ClasificacionAdherente.objects.get(nombre="Docente")
    asociado = Asociado.objects.create(
        nombre="Ana",
        apellido="Pérez",
        dni="40111222",
        tipo=Asociado.TIPO_ASOCIADO,
        curso_actual=curso,
        fecha_alta=date(2026, 8, 1),
        fecha_inicio_cobro=date(2026, 8, 1),
    )
    form = AsociadoGestionForm(
        data={
            **datos_base(
                tipo=Asociado.TIPO_ADHERENTE,
                curso_actual=curso.pk,
                clasificacion_adherente=clasificacion.pk,
            ),
            "fecha_inicio_cobro": "2026-08-01",
        },
        instance=asociado,
    )

    assert form.is_valid(), form.errors
    assert form.cleaned_data["curso_actual"] is None
    assert form.cleaned_data["clasificacion_adherente"] == clasificacion
