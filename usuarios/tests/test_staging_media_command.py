from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

from comercios.models import ActividadComercial, Comercio
from contenidos.models import Publicidad
from config.database_identity import storage_fingerprint
from usuarios.management.commands import copiar_media_staging


STAGING_MEDIA_SETTINGS = override_settings(
    UNI2_DEPLOYMENT_ENVIRONMENT="staging",
    UNI2_STAGING_DATABASE_LABEL="uni2-staging",
    AWS_STORAGE_BUCKET_NAME="uni2-staging-media",
    STORAGES={"default": {"BACKEND": "storages.backends.s3.S3Storage"}},
)


class FakeStorage:
    def __init__(self, existing=()):
        self.files = {path: b"existente" for path in existing}

    def exists(self, path):
        return path in self.files

    def save(self, path, content):
        self.files[path] = content.read()
        return path

    def delete(self, path):
        self.files.pop(path, None)


class FakeResponse:
    def __init__(self, url, content=b"imagen"):
        self.url = url
        self.content = content
        self.headers = {"Content-Type": "image/jpeg"}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def geturl(self):
        return self.url

    def read(self, size):
        return self.content[:size]


def test_huella_storage_no_necesita_claves_de_acceso():
    output = StringIO()

    call_command(
        "huella_storage",
        bucket="uni2-staging-media",
        endpoint="https://cuenta.r2.cloudflarestorage.com/",
        stdout=output,
    )

    assert output.getvalue().strip() == storage_fingerprint(
        "uni2-staging-media",
        "https://cuenta.r2.cloudflarestorage.com/",
    )


def create_referenced_media():
    actividad = ActividadComercial.objects.create(nombre="Librería")
    Comercio.objects.create(
        nombre="Comercio con foto",
        actividad_comercial=actividad,
        beneficio_texto="10% de descuento",
        estado=Comercio.ESTADO_FIRMADO,
        foto="comercios/comercio.jpg",
    )
    Publicidad.objects.create(
        titulo="Publicidad con foto",
        descripcion="Descripción",
        etiqueta_principal="Beneficio",
        etiqueta_secundaria="10% OFF",
        foto="publicidades/publicidad.jpg",
    )


@pytest.mark.django_db
@STAGING_MEDIA_SETTINGS
def test_copiar_media_staging_informa_el_plan_sin_escribir(monkeypatch):
    create_referenced_media()
    storage = FakeStorage()
    monkeypatch.setattr(copiar_media_staging, "default_storage", storage)
    output = StringIO()

    call_command(
        "copiar_media_staging",
        source_base_url="https://media-produccion.example.test",
        confirm_target="uni2-staging",
        stdout=output,
    )

    assert storage.files == {}
    assert "Archivos referenciados: 2" in output.getvalue()
    assert "Repetí el comando con --confirmar" in output.getvalue()


@pytest.mark.django_db
@STAGING_MEDIA_SETTINGS
def test_copiar_media_staging_copia_solo_faltantes_y_conserva_las_rutas(monkeypatch):
    create_referenced_media()
    storage = FakeStorage(existing={"comercios/comercio.jpg"})
    requested_urls = []

    def fake_urlopen(request, timeout):
        requested_urls.append(request.full_url)
        assert timeout == 30
        return FakeResponse(request.full_url)

    monkeypatch.setattr(copiar_media_staging, "default_storage", storage)
    monkeypatch.setattr(copiar_media_staging, "urlopen", fake_urlopen)
    output = StringIO()

    call_command(
        "copiar_media_staging",
        source_base_url="https://media-produccion.example.test/",
        confirm_target="uni2-staging",
        confirmar=True,
        stdout=output,
    )

    assert requested_urls == [
        "https://media-produccion.example.test/publicidades/publicidad.jpg"
    ]
    assert storage.files == {
        "comercios/comercio.jpg": b"existente",
        "publicidades/publicidad.jpg": b"imagen",
    }
    assert "1 archivos copiados, 1 ya existentes y 0 errores" in output.getvalue()


@pytest.mark.django_db
@STAGING_MEDIA_SETTINGS
def test_copiar_media_staging_rechaza_un_destino_no_confirmado():
    with pytest.raises(CommandError, match="confirmación no coincide"):
        call_command(
            "copiar_media_staging",
            source_base_url="https://media-produccion.example.test",
            confirm_target="otro-entorno",
            confirmar=True,
        )


@pytest.mark.django_db
@override_settings(
    UNI2_DEPLOYMENT_ENVIRONMENT="staging",
    UNI2_STAGING_DATABASE_LABEL="uni2-staging",
)
def test_copiar_media_staging_exige_un_bucket_remoto():
    with pytest.raises(CommandError, match="no tiene un bucket media remoto"):
        call_command(
            "copiar_media_staging",
            source_base_url="https://media-produccion.example.test",
            confirm_target="uni2-staging",
            confirmar=True,
        )


@pytest.mark.django_db
@STAGING_MEDIA_SETTINGS
def test_copiar_media_staging_rechaza_un_origen_inseguro():
    with pytest.raises(CommandError, match="URL HTTPS sin credenciales"):
        call_command(
            "copiar_media_staging",
            source_base_url="http://media-produccion.example.test",
            confirm_target="uni2-staging",
            confirmar=True,
        )
