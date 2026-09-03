from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from asociados.models import (
    Asociado,
    ClasificacionAdherente,
    Curso,
    LimiteSolicitudPublica,
    SolicitudAsociacion,
)


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
    return ClasificacionAdherente.objects.get(nombre="Familiar")


def datos_solicitud(**overrides):
    datos = {
        "nombre": "Ana María",
        "apellido": "O'Connor",
        "dni": "48.123.456",
        "email": "ana@example.com",
        "telefono": "+54 299 555-0192",
        "direccion": "Los Maitenes 142",
        "es_estudiante_cet3": True,
        "token_seguimiento_hash": "a" * 64,
        "token_seguimiento_vence_en": timezone.now() + timedelta(days=30),
    }
    datos.update(overrides)
    return datos


def test_solicitud_muestra_estado_datos_aprobados():
    solicitud = SolicitudAsociacion(
        estado=SolicitudAsociacion.ESTADO_DATOS_APROBADOS
    )

    assert solicitud.get_estado_display() == "Datos aprobados"


@pytest.mark.django_db
def test_solicitud_deriva_asociado_y_exige_curso(curso):
    solicitud = SolicitudAsociacion(**datos_solicitud(curso_actual=curso))

    solicitud.full_clean()

    assert solicitud.tipo == Asociado.TIPO_ASOCIADO
    assert solicitud.dni_normalizado == "48123456"
    assert solicitud.clasificacion_adherente is None


@pytest.mark.django_db
def test_solicitud_deriva_adherente_y_exige_clasificacion(clasificacion):
    solicitud = SolicitudAsociacion(
        **datos_solicitud(
            dni="BO-12345-A",
            es_estudiante_cet3=False,
            clasificacion_adherente=clasificacion,
        )
    )

    solicitud.full_clean()

    assert solicitud.tipo == Asociado.TIPO_ADHERENTE
    assert solicitud.dni_normalizado == "BO12345A"
    assert solicitud.curso_actual is None


@pytest.mark.django_db
def test_solicitud_rechaza_dato_institucional_inactivo(curso, clasificacion):
    curso.activo = False
    curso.save(update_fields=("activo",))
    clasificacion.activa = False
    clasificacion.save(update_fields=("activa",))

    with pytest.raises(ValidationError, match="curso"):
        SolicitudAsociacion(**datos_solicitud(curso_actual=curso)).full_clean()
    with pytest.raises(ValidationError, match="clasificación"):
        SolicitudAsociacion(
            **datos_solicitud(
                es_estudiante_cet3=False,
                clasificacion_adherente=clasificacion,
            )
        ).full_clean()


@pytest.mark.django_db
def test_solicitud_cancelada_permite_mismo_documento_y_correo(curso):
    SolicitudAsociacion.objects.create(
        **datos_solicitud(
            curso_actual=curso,
            estado=SolicitudAsociacion.ESTADO_CANCELADA,
        )
    )

    nueva = SolicitudAsociacion.objects.create(
        **datos_solicitud(
            curso_actual=curso,
            token_seguimiento_hash="b" * 64,
        )
    )

    assert nueva.pk is not None


@pytest.mark.django_db(transaction=True)
def test_solicitud_no_cancelada_no_repite_documento_normalizado(curso):
    primera = SolicitudAsociacion(**datos_solicitud(curso_actual=curso))
    primera.save()

    duplicada = SolicitudAsociacion(
        **datos_solicitud(
            dni="48123456",
            curso_actual=curso,
            token_seguimiento_hash="b" * 64,
        )
    )
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            duplicada.save()


@pytest.mark.django_db(transaction=True)
def test_limite_publico_es_unico_por_accion_clave_y_ventana():
    ahora = timezone.now().replace(microsecond=0)
    datos = {
        "accion": "crear_solicitud",
        "clave_hash": "c" * 64,
        "ventana_inicio": ahora,
    }
    LimiteSolicitudPublica.objects.create(**datos)

    with pytest.raises(IntegrityError):
        LimiteSolicitudPublica.objects.create(**datos)
