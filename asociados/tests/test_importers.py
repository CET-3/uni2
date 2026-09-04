import logging
from datetime import date

import pytest
from django.core import mail

from asociados.importers import PadronPreview, _normalize_row, import_padron_preview
from asociados.models import Asociado, ClasificacionAdherente
from comunicaciones.models import Comunicacion
from usuarios.services import ensure_default_groups


def _padron_row(fila_origen, dni, apellido="Leyes", nombre="Lena"):
    return {
        "fila_origen": fila_origen,
        "apellido": apellido,
        "nombre": nombre,
        "dni": dni,
        "tipo": Asociado.TIPO_ADHERENTE,
        "curso": "",
        "clasificacion_adherente": ClasificacionAdherente.NOMBRE_SIN_CLASIFICAR,
        "curso_anio": "",
        "curso_division": "",
        "division": "",
        "turno": "",
        "telefono": "",
        "email": "",
        "direccion": "",
    }


@pytest.mark.django_db
def test_import_padron_preview_loguea_avance_y_resumen(caplog):
    ensure_default_groups()
    preview = PadronPreview(
        importables=[
            _padron_row(2, "52328996"),
            _padron_row(3, "52536191", apellido="Darosa", nombre="Joaquin"),
        ],
        revisar=[{"fila_origen": 4}],
        no_importar_count=1,
    )
    preview.importables[0]["email"] = "lena@example.com"

    caplog.set_level(logging.INFO, logger="asociados.importers")

    import_padron_preview(preview, date(2026, 6, 23))

    mensajes = [record.getMessage() for record in caplog.records]
    assert "Importacion de padron inicial iniciada: 2 filas importables." in mensajes
    assert "Importacion de padron inicial: 2/2 filas procesadas." in mensajes
    assert (
        "Importacion de padron inicial finalizada: 2 creados, 0 actualizados, "
        "0 cursos creados, 2 omitidos, 0 errores."
    ) in mensajes
    assert not Comunicacion.objects.filter(tipo="alta_usuario").exists()
    assert len(mail.outbox) == 0


def _raw_row(*, tipo="Adherente", curso="profe", dni="40111222"):
    return {
        "fila_origen": 2,
        "numero_asociado": "1",
        "apellido_nombre_original": "Pérez Ana",
        "curso_original": curso,
        "ciclo_original": "",
        "tipo_original": tipo,
        "dni": dni,
        "telefono": "",
        "email": "",
        "direccion": "",
        "tiene_datos_persona": True,
        "tiene_alguna_celda": True,
    }


@pytest.mark.django_db
def test_padron_normaliza_alias_de_cargo_para_adherente():
    row = _normalize_row(_raw_row(curso="profesora"), {"40111222": 1})

    assert row["estado_importacion"] == "IMPORTAR"
    assert row["clasificacion_adherente"] == "Docente"
    assert row["curso"] == ""


@pytest.mark.django_db
def test_padron_acepta_clasificacion_administrada_por_nombre():
    ClasificacionAdherente.objects.create(nombre="Cooperadora", activa=True, orden=20)

    row = _normalize_row(_raw_row(curso="cooperadora"), {"40111222": 1})

    assert row["estado_importacion"] == "IMPORTAR"
    assert row["clasificacion_adherente"] == "Cooperadora"


@pytest.mark.django_db
def test_padron_no_convierte_asociado_con_cargo_en_adherente():
    row = _normalize_row(_raw_row(tipo="Activo", curso="profesor"), {"40111222": 1})

    assert row["estado_importacion"] == "REVISAR"
    assert row["tipo"] == Asociado.TIPO_ASOCIADO
    assert row["curso"] == ""
    assert "curso incompleto" in row["observaciones"]


@pytest.mark.django_db
def test_reimportacion_actualiza_clasificacion_por_dni():
    sin_clasificar = ClasificacionAdherente.objects.get(nombre="Sin clasificar")
    docente = ClasificacionAdherente.objects.get(nombre="Docente")
    existente = Asociado.objects.create(
        nombre="Ana",
        apellido="Pérez",
        dni="40111222",
        tipo=Asociado.TIPO_ADHERENTE,
        clasificacion_adherente=sin_clasificar,
        fecha_alta=date(2026, 3, 1),
        fecha_inicio_cobro=date(2026, 3, 1),
    )
    preview = PadronPreview(importables=[_padron_row(2, existente.dni)])
    preview.importables[0]["clasificacion_adherente"] = "Docente"

    result = import_padron_preview(preview, date(2026, 8, 1))

    existente.refresh_from_db()
    assert result.actualizados == 1
    assert existente.clasificacion_adherente == docente
