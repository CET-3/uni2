import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from comercios.models import ActividadComercial, Comercio
from comercios.selectors import get_rubros_con_comercios


@pytest.fixture
def rubro():
    return ActividadComercial.objects.create(nombre="Gastronomía")


@pytest.fixture
def foto():
    return SimpleUploadedFile("com.jpg", b"content", content_type="image/jpeg")


@pytest.mark.django_db
def test_rubros_con_comercios_incluye_fotos(rubro, foto):
    for i in range(3):
        Comercio.objects.create(
            nombre=f"Com {i}",
            actividad_comercial=rubro,
            beneficio_texto="10% off",
            estado=Comercio.ESTADO_FIRMADO,
            orden=i + 2,
            direccion=f"Calle {i}",
            foto=foto,
        )

    qs = get_rubros_con_comercios()
    rubro_result = qs.get(nombre="Gastronomía")
    assert len(rubro_result.comercios_con_foto) == 3


@pytest.mark.django_db
def test_rubros_sin_comercios_firmados_no_aparecen(rubro):
    qs = get_rubros_con_comercios()
    assert rubro not in qs


@pytest.mark.django_db
def test_rubro_con_menos_de_3_comercios_con_foto(rubro, foto):
    Comercio.objects.create(
        nombre="Único",
        actividad_comercial=rubro,
        beneficio_texto="15% off",
        estado=Comercio.ESTADO_FIRMADO,
        orden=1,
        direccion="Calle 1",
        foto=foto,
    )

    qs = get_rubros_con_comercios()
    rubro_result = qs.get(nombre="Gastronomía")
    assert len(rubro_result.comercios_con_foto) == 1


@pytest.mark.django_db
def test_cada_rubro_recibe_sus_tres_comercios_con_foto(foto):
    gastronomia = ActividadComercial.objects.create(nombre="Gastronomía")
    libreria = ActividadComercial.objects.create(nombre="Librería")

    for orden, rubro in enumerate([gastronomia, libreria], start=1):
        for numero in range(3):
            Comercio.objects.create(
                nombre=f"{rubro.nombre} {numero}",
                actividad_comercial=rubro,
                beneficio_texto="10% off",
                estado=Comercio.ESTADO_FIRMADO,
                orden=orden * 10 + numero,
                direccion=f"Calle {orden}-{numero}",
                foto=foto,
            )

    qs = get_rubros_con_comercios()

    assert len(qs.get(nombre="Gastronomía").comercios_con_foto) == 3
    assert len(qs.get(nombre="Librería").comercios_con_foto) == 3
