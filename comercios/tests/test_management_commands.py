from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from comercios.models import Comercio
from comercios.tests.xlsx_helpers import build_comercios_xlsx


def comercio_row(**overrides):
    row = {
        "COMERCIO": "Comercio inicial",
        "CÓDIGO": 99,
        "ACTIVIDAD COMERCIAL": "Venta online",
        "DESCUENTO": "10% en compras",
        "INSTAGRAM": "https://www.instagram.com/comercio.inicial/",
        "UBICACIÓN": "",
        "DESCRIPCIÓN": "Productos disponibles por internet.",
    }
    row.update(overrides)
    return row


def save_xlsx(tmp_path, rows):
    path = tmp_path / "comercios.xlsx"
    path.write_bytes(build_comercios_xlsx(rows).getvalue())
    return path


@pytest.mark.django_db
def test_importar_comercios_xlsx_analiza_sin_guardar(tmp_path):
    path = save_xlsx(tmp_path, [comercio_row()])
    output = StringIO()

    call_command("importar_comercios_xlsx", str(path), stdout=output)

    assert Comercio.objects.count() == 0
    assert "Comercios encontrados: 1" in output.getvalue()
    assert "Análisis finalizado sin guardar datos" in output.getvalue()


@pytest.mark.django_db
def test_importar_comercios_xlsx_confirma_la_importacion(tmp_path):
    path = save_xlsx(tmp_path, [comercio_row()])
    output = StringIO()

    call_command("importar_comercios_xlsx", str(path), confirmar=True, stdout=output)

    comercio = Comercio.objects.get()
    assert comercio.nombre == "Comercio inicial"
    assert comercio.orden == 0
    assert comercio.estado == Comercio.ESTADO_FIRMADO
    assert "Comercios creados: 1" in output.getvalue()


@pytest.mark.django_db
def test_importar_comercios_xlsx_no_guarda_si_hay_errores(tmp_path):
    path = save_xlsx(tmp_path, [comercio_row(INSTAGRAM="@comercio.inicial")])
    output = StringIO()

    with pytest.raises(CommandError, match="No se modificó la base de datos"):
        call_command(
            "importar_comercios_xlsx",
            str(path),
            confirmar=True,
            stdout=output,
        )

    assert Comercio.objects.count() == 0
    assert "INSTAGRAM debe contener una URL completa" in output.getvalue()
