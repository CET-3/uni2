import pytest
from django.core.exceptions import FieldDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile

from comercios.models import ActividadComercial, Comercio


def test_actividad_comercial_tiene_descripcion_publica_opcional():
    descripcion = ActividadComercial._meta.get_field("descripcion")

    assert descripcion.blank is True
    assert descripcion.null is False


def test_comercio_tiene_descripcion_obligatoria_y_direccion_opcional():
    descripcion = Comercio._meta.get_field("descripcion")
    direccion = Comercio._meta.get_field("direccion")

    assert descripcion.blank is False
    assert descripcion.null is False
    assert direccion.blank is True
    assert direccion.null is False


def test_comercio_no_conserva_notas_ni_flyer_disponible():
    with pytest.raises(FieldDoesNotExist):
        Comercio._meta.get_field("notas")

    with pytest.raises(FieldDoesNotExist):
        Comercio._meta.get_field("flyer_disponible")


@pytest.mark.django_db
def test_comercio_foto_optional():
    actividad = ActividadComercial.objects.create(nombre="Test")
    comercio = Comercio.objects.create(
        nombre="Test",
        descripcion="Descripción del comercio de prueba.",
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
