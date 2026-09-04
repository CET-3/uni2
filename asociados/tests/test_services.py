from datetime import date
from io import StringIO

import pytest
from django.core import mail

from asociados.models import Asociado, ClasificacionAdherente, Curso
from asociados.services import (
    calculate_fecha_inicio_cobro,
    create_asociado,
    dar_baja_asociado,
    import_asociados_from_csv,
)
from comunicaciones.models import Comunicacion


@pytest.fixture
def curso():
    return Curso.objects.create(anio="1ro", curso="1ra", division=Curso.DIVISION_CB, turno=Curso.TURNO_TM)


@pytest.mark.django_db
def test_curso_se_muestra_con_constantes_cortas(curso):
    assert str(curso) == "1ro 1ra CB TM"


@pytest.mark.django_db
def test_alta_de_asociado_comienza_dos_meses_antes(curso):
    asociado = create_asociado(
        nombre="Juan",
        apellido="Perez",
        dni="30123456",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 5, 10),
        curso_actual=curso,
    )
    assert asociado.fecha_inicio_cobro == date(2026, 3, 1)


@pytest.mark.django_db
def test_create_asociado_no_programa_correo_por_defecto():
    asociado = create_asociado(
        nombre="Ana",
        apellido="Flores",
        dni="48123456",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 9, 4),
        email="ana@example.com",
    )

    assert asociado.usuario_id is not None
    assert not Comunicacion.objects.filter(tipo="alta_usuario").exists()


@pytest.mark.django_db
def test_create_asociado_programa_correo_con_opt_in():
    asociado = create_asociado(
        nombre="Ana",
        apellido="Flores",
        dni="48123456",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 9, 4),
        email="ana@example.com",
        enviar_correo_alta=True,
    )

    assert asociado.usuario_id is not None
    assert Comunicacion.objects.filter(
        tipo="alta_usuario",
        origen_entidad="asociados.Asociado",
        origen_id=str(asociado.pk),
    ).count() == 1


@pytest.mark.django_db
def test_create_asociado_con_opt_in_y_sin_email_crea_usuario_sin_correo():
    asociado = create_asociado(
        nombre="Ana",
        apellido="Flores",
        dni="48123456",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 9, 4),
        enviar_correo_alta=True,
    )

    assert asociado.usuario_id is not None
    assert not Comunicacion.objects.filter(tipo="alta_usuario").exists()


@pytest.mark.django_db
def test_import_asociados_csv_con_email_no_programa_correo_de_alta():
    archivo = StringIO(
        "nombre,apellido,dni,tipo,fecha_alta,email,telefono\n"
        "Ana,Flores,48123456,asociado,2026-09-04,ana@example.com,2995550192\n"
    )

    resultado = import_asociados_from_csv(archivo)

    assert resultado.created == 1
    assert not resultado.errors
    assert not Comunicacion.objects.filter(tipo="alta_usuario").exists()
    assert len(mail.outbox) == 0


@pytest.mark.parametrize(
    ("fecha_alta", "tipo", "fecha_esperada"),
    [
        (date(2026, 5, 1), Asociado.TIPO_ASOCIADO, date(2026, 3, 1)),
        (date(2026, 5, 15), Asociado.TIPO_ASOCIADO, date(2026, 3, 1)),
        (date(2026, 5, 16), Asociado.TIPO_ASOCIADO, date(2026, 3, 1)),
        (date(2026, 5, 31), Asociado.TIPO_ASOCIADO, date(2026, 3, 1)),
        (date(2026, 1, 10), Asociado.TIPO_ASOCIADO, date(2025, 11, 1)),
        (date(2026, 2, 28), Asociado.TIPO_ASOCIADO, date(2025, 12, 1)),
        (date(2026, 5, 1), Asociado.TIPO_ADHERENTE, date(2026, 5, 1)),
        (date(2026, 5, 15), Asociado.TIPO_ADHERENTE, date(2026, 5, 1)),
        (date(2026, 5, 16), Asociado.TIPO_ADHERENTE, date(2026, 5, 1)),
        (date(2026, 5, 31), Asociado.TIPO_ADHERENTE, date(2026, 5, 1)),
    ],
)
def test_calcula_fecha_inicio_cobro_segun_tipo(fecha_alta, tipo, fecha_esperada):
    assert calculate_fecha_inicio_cobro(fecha_alta, tipo) == fecha_esperada


@pytest.mark.django_db
def test_fecha_inicio_cobro_personalizada():
    clasificacion = ClasificacionAdherente.objects.get(nombre="Familiar")
    asociado = create_asociado(
        nombre="Lia",
        apellido="Mora",
        dni="32123456",
        tipo=Asociado.TIPO_ADHERENTE,
        clasificacion_adherente=clasificacion,
        fecha_alta=date(2026, 5, 20),
        fecha_inicio_cobro=date(2026, 8, 1),
    )
    assert asociado.fecha_inicio_cobro == date(2026, 8, 1)


@pytest.mark.django_db
def test_crear_adherente_limpia_curso_y_guarda_clasificacion(curso):
    clasificacion = ClasificacionAdherente.objects.get(nombre="Docente")

    asociado = create_asociado(
        nombre="Lia",
        apellido="Mora",
        dni="32123457",
        tipo=Asociado.TIPO_ADHERENTE,
        fecha_alta=date(2026, 5, 20),
        curso_actual=curso,
        clasificacion_adherente=clasificacion,
    )

    assert asociado.curso_actual is None
    assert asociado.clasificacion_adherente == clasificacion


@pytest.mark.django_db
def test_crear_adherente_sin_clasificacion_usa_valor_transitorio():
    asociado = create_asociado(
        nombre="Lia",
        apellido="Mora",
        dni="32123458",
        tipo=Asociado.TIPO_ADHERENTE,
        fecha_alta=date(2026, 5, 20),
    )

    assert asociado.clasificacion_adherente.nombre == "Sin clasificar"


@pytest.mark.django_db
def test_baja_de_asociado(curso):
    asociado = create_asociado(
        nombre="Rocio",
        apellido="Diaz",
        dni="33123456",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 3, 10),
        curso_actual=curso,
    )

    dar_baja_asociado(asociado, date(2026, 6, 1), "Mudanza")
    asociado.refresh_from_db()

    assert asociado.estado == Asociado.ESTADO_INACTIVO
    assert asociado.fecha_baja == date(2026, 6, 1)


@pytest.mark.django_db
def test_numero_asociado_se_genera_automaticamente_tambien_fuera_del_service():
    asociado = Asociado.objects.create(
        nombre="Mara",
        apellido="Rios",
        dni="36111111",
        tipo=Asociado.TIPO_ADHERENTE,
        fecha_alta=date(2026, 5, 22),
        fecha_inicio_cobro=date(2026, 5, 1),
    )

    assert asociado.numero_asociado == 1
