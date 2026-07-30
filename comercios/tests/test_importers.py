import pytest

from comercios.importers import analyze_comercios_xlsx, import_comercios_preview
from comercios.models import ActividadComercial, Comercio
from comercios.tests.xlsx_helpers import COMERCIOS_HEADERS, build_comercios_xlsx


def comercio_row(**overrides):
    row = {
        "COMERCIO": "Librería de prueba",
        "CÓDIGO": 25,
        "ACTIVIDAD COMERCIAL": "Educación",
        "DESCUENTO": 0.15,
        "INSTAGRAM": "https://www.instagram.com/libreria.prueba/",
        "UBICACIÓN": "",
        "DESCRIPCIÓN": "Útiles y materiales para estudiar.",
    }
    row.update(overrides)
    return row


def test_analyze_comercios_mapea_campos_y_foto_sin_usar_codigo():
    xlsx_file = build_comercios_xlsx([comercio_row()], image_rows=[2])

    preview = analyze_comercios_xlsx(xlsx_file)

    assert preview.es_valida
    assert preview.cantidad_actividades == 1
    assert preview.cantidad_fotos == 1
    assert len(preview.filas) == 1
    row = preview.filas[0]
    assert row.nombre == "Librería de prueba"
    assert row.actividad_comercial == "Educación"
    assert row.beneficio_texto == "15%"
    assert row.url_presencia_web == "https://www.instagram.com/libreria.prueba/"
    assert row.direccion == ""
    assert row.descripcion == "Útiles y materiales para estudiar."
    assert row.foto.extension == "png"
    assert not hasattr(row, "codigo")
    assert not hasattr(row, "orden")


def test_analyze_comercios_exige_url_completa():
    xlsx_file = build_comercios_xlsx([comercio_row(INSTAGRAM="@libreria.prueba")])

    preview = analyze_comercios_xlsx(xlsx_file)

    assert not preview.es_valida
    assert preview.errores == [
        "Fila 2: INSTAGRAM debe contener una URL completa http:// o https://."
    ]


def test_analyze_comercios_permite_presencia_web_vacia():
    xlsx_file = build_comercios_xlsx([comercio_row(INSTAGRAM="")])

    preview = analyze_comercios_xlsx(xlsx_file)

    assert preview.es_valida
    assert preview.filas[0].url_presencia_web == ""


def test_analyze_comercios_exige_los_encabezados_esperados():
    headers = [header for header in COMERCIOS_HEADERS if header != "DESCRIPCIÓN"]
    xlsx_file = build_comercios_xlsx([comercio_row()], headers=headers)

    with pytest.raises(ValueError, match="DESCRIPCION"):
        analyze_comercios_xlsx(xlsx_file)


def test_analyze_comercios_detecta_descripcion_faltante_y_nombre_repetido():
    xlsx_file = build_comercios_xlsx(
        [
            comercio_row(**{"DESCRIPCIÓN": ""}),
            comercio_row(COMERCIO="  LIBRERIA DE PRUEBA  "),
        ]
    )

    preview = analyze_comercios_xlsx(xlsx_file)

    assert not preview.es_valida
    assert "Fila 2: falta DESCRIPCIÓN." in preview.errores
    assert (
        'Fila 3: el comercio "LIBRERIA DE PRUEBA" está repetido; también aparece en la fila 2.'
        in preview.errores
    )


@pytest.mark.django_db
def test_import_comercios_crea_y_actualiza_sin_duplicar(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    preview = analyze_comercios_xlsx(
        build_comercios_xlsx([comercio_row()], image_rows=[2])
    )

    first_result = import_comercios_preview(preview)

    comercio = Comercio.objects.get()
    assert first_result.comercios_creados == 1
    assert first_result.comercios_actualizados == 0
    assert first_result.actividades_creadas == 1
    assert first_result.fotos_asignadas == 1
    assert ActividadComercial.objects.count() == 1
    assert comercio.actividad_comercial.nombre == "Educación"
    assert comercio.descripcion == "Útiles y materiales para estudiar."
    assert comercio.beneficio_texto == "15%"
    assert comercio.estado == Comercio.ESTADO_FIRMADO
    assert comercio.orden == 0
    assert comercio.direccion == ""
    assert comercio.url_presencia_web == "https://www.instagram.com/libreria.prueba/"
    assert comercio.foto.name.startswith("comercios/importacion/libreria-de-prueba-")
    assert (tmp_path / comercio.foto.name).exists()
    original_photo_name = comercio.foto.name

    second_result = import_comercios_preview(preview)

    comercio.refresh_from_db()
    assert Comercio.objects.count() == 1
    assert ActividadComercial.objects.count() == 1
    assert second_result.comercios_creados == 0
    assert second_result.comercios_actualizados == 1
    assert second_result.actividades_creadas == 0
    assert second_result.fotos_asignadas == 0
    assert comercio.foto.name == original_photo_name


@pytest.mark.django_db
def test_import_comercios_no_reemplaza_foto_si_la_fila_no_tiene_imagen(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    preview_with_photo = analyze_comercios_xlsx(
        build_comercios_xlsx([comercio_row()], image_rows=[2])
    )
    import_comercios_preview(preview_with_photo)
    original_photo_name = Comercio.objects.get().foto.name

    preview_without_photo = analyze_comercios_xlsx(build_comercios_xlsx([comercio_row()]))
    result = import_comercios_preview(preview_without_photo)

    comercio = Comercio.objects.get()
    assert result.comercios_actualizados == 1
    assert result.fotos_asignadas == 0
    assert comercio.foto.name == original_photo_name
