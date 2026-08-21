from datetime import date

import pytest

from asociados.models import Asociado, ClasificacionAdherente, Curso
from gestion.forms import AsociadoAltaForm, AsociadoGestionForm


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
def test_alta_no_ofrece_sin_clasificar():
    form = AsociadoAltaForm()

    nombres = list(form.fields["clasificacion_adherente"].queryset.values_list("nombre", flat=True))

    assert "Docente" in nombres
    assert "Sin clasificar" not in nombres


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
