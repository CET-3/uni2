import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from comercios.models import ActividadComercial, Comercio


@pytest.mark.django_db
def test_comercio_foto_optional():
    actividad = ActividadComercial.objects.create(nombre="Test")
    comercio = Comercio.objects.create(
        nombre="Test",
        actividad_comercial=actividad,
        beneficio_texto="10% off",
        estado=Comercio.ESTADO_FIRMADO,
        orden=1,
        direccion="Calle 123",
    )
    assert comercio.foto.name is None

    foto = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
    comercio.foto = foto
    comercio.save()
    assert comercio.foto.name is not None
