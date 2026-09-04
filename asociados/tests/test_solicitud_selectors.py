import hashlib
from datetime import timedelta

import pytest
from django.utils import timezone

from asociados.models import Curso, SolicitudAsociacion
from asociados.selectors import obtener_solicitud_por_token
from asociados.services import rotar_token_seguimiento


@pytest.mark.django_db
def test_obtener_solicitud_por_token_solo_acepta_el_ultimo_vigente():
    curso = Curso.objects.create(
        anio="1ro",
        curso="1ra",
        division=Curso.DIVISION_CB,
        turno=Curso.TURNO_TM,
    )
    solicitud = SolicitudAsociacion.objects.create(
        nombre="Ana",
        apellido="Flores",
        dni="48123456",
        email="ana@example.com",
        telefono="2995550192",
        direccion="Los Maitenes 142",
        es_estudiante_cet3=True,
        curso_actual=curso,
        token_seguimiento_hash="a" * 64,
        token_seguimiento_vence_en=timezone.now() + timedelta(days=30),
    )

    token_anterior = rotar_token_seguimiento(solicitud)
    token_nuevo = rotar_token_seguimiento(solicitud)

    assert obtener_solicitud_por_token(token_anterior) is None
    assert obtener_solicitud_por_token(token_nuevo) == solicitud


@pytest.mark.django_db
def test_obtener_solicitud_por_token_rechaza_un_enlace_vencido():
    token = "enlace-vencido"
    curso = Curso.objects.create(
        anio="1ro",
        curso="1ra",
        division=Curso.DIVISION_CB,
        turno=Curso.TURNO_TM,
    )
    solicitud = SolicitudAsociacion.objects.create(
        nombre="Ana",
        apellido="Flores",
        dni="48123456",
        email="ana@example.com",
        telefono="2995550192",
        direccion="Los Maitenes 142",
        es_estudiante_cet3=True,
        curso_actual=curso,
        token_seguimiento_hash=hashlib.sha256(token.encode()).hexdigest(),
        token_seguimiento_vence_en=timezone.now() - timedelta(seconds=1),
    )

    assert obtener_solicitud_por_token(token) is None
