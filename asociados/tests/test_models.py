from datetime import date

import pytest
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError

from asociados.models import Asociado, ClasificacionAdherente, Curso


@pytest.fixture
def curso():
    return Curso.objects.create(
        anio="1ro",
        curso="1ra",
        division=Curso.DIVISION_CB,
        turno=Curso.TURNO_TM,
    )


@pytest.fixture
def clasificacion():
    return ClasificacionAdherente.objects.get(nombre="Docente")


def asociado_base(**overrides):
    data = {
        "nombre": "Ana",
        "apellido": "Pérez",
        "dni": "40111222",
        "tipo": Asociado.TIPO_ASOCIADO,
        "fecha_alta": date(2026, 8, 1),
        "fecha_inicio_cobro": date(2026, 8, 1),
    }
    data.update(overrides)
    return Asociado(**data)


@pytest.mark.django_db
def test_clasificacion_adherente_es_legible_y_ordenable():
    segunda = ClasificacionAdherente.objects.get(nombre="Preceptor")
    primera = ClasificacionAdherente.objects.get(nombre="Docente")

    assert str(primera) == "Docente"
    assert list(ClasificacionAdherente.objects.all()[:2]) == [primera, segunda]


@pytest.mark.django_db
def test_clasificacion_usada_no_se_puede_eliminar(clasificacion):
    Asociado.objects.create(
        nombre="Ana",
        apellido="Pérez",
        dni="40111222",
        tipo=Asociado.TIPO_ADHERENTE,
        clasificacion_adherente=clasificacion,
        fecha_alta=date(2026, 8, 1),
        fecha_inicio_cobro=date(2026, 8, 1),
    )

    with pytest.raises(ProtectedError):
        clasificacion.delete()


@pytest.mark.django_db
def test_asociado_requiere_curso_y_rechaza_clasificacion(curso, clasificacion):
    sin_curso = asociado_base()
    with pytest.raises(ValidationError, match="curso"):
        sin_curso.full_clean()

    con_clasificacion = asociado_base(
        curso_actual=curso,
        clasificacion_adherente=clasificacion,
    )
    with pytest.raises(ValidationError, match="clasificación"):
        con_clasificacion.full_clean()


@pytest.mark.django_db
def test_adherente_requiere_clasificacion_y_rechaza_curso(curso, clasificacion):
    sin_clasificacion = asociado_base(tipo=Asociado.TIPO_ADHERENTE)
    with pytest.raises(ValidationError, match="clasificación"):
        sin_clasificacion.full_clean()

    con_curso = asociado_base(
        tipo=Asociado.TIPO_ADHERENTE,
        curso_actual=curso,
        clasificacion_adherente=clasificacion,
    )
    with pytest.raises(ValidationError, match="curso"):
        con_curso.full_clean()


@pytest.mark.django_db
def test_dato_institucional_usa_curso_o_clasificacion(curso, clasificacion):
    asociado = asociado_base(curso_actual=curso)
    adherente = asociado_base(
        tipo=Asociado.TIPO_ADHERENTE,
        clasificacion_adherente=clasificacion,
    )

    assert asociado.get_dato_institucional() == ("Curso", "1ro 1ra CB TM")
    assert adherente.get_dato_institucional() == ("Clasificación", "Docente")
