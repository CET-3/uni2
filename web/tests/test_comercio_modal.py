import pytest
from django.urls import reverse

from comercios.models import ActividadComercial, Comercio


@pytest.fixture
def actividad():
    return ActividadComercial.objects.create(nombre="Librería")


@pytest.fixture
def comercio_firmado(actividad):
    return Comercio.objects.create(
        nombre="Librería Sur",
        descripcion="Útiles y libros escolares.",
        direccion="Mitre 123",
        telefono="299 4000000",
        email="libreria@example.com",
        url_presencia_web="https://example.com/libreria",
        actividad_comercial=actividad,
        beneficio_texto="10% en útiles",
        estado=Comercio.ESTADO_FIRMADO,
    )


@pytest.mark.django_db
def test_modal_comercio_firmado_muestra_solo_datos_publicos(client, comercio_firmado):
    response = client.get(
        reverse("web:comercio_detalle_modal", args=[comercio_firmado.pk])
    )

    content = response.content.decode()
    assert response.status_code == 200
    assert response.template_name == ["web/_comercio_modal_content.html"]
    assert "Librería Sur" in content
    assert "10% en útiles" in content
    assert "Mitre 123" in content
    assert "299 4000000" in content
    assert "libreria@example.com" in content
    assert reverse("web:comercio_detalle", args=[comercio_firmado.pk]) in content
    assert "Ver ficha completa" in content
    assert "breadcrumb" not in content.lower()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "estado",
    [Comercio.ESTADO_PENDIENTE, Comercio.ESTADO_VENCIDO, Comercio.ESTADO_BAJA],
)
def test_modal_no_publica_comercio_sin_convenio_firmado(client, actividad, estado):
    comercio = Comercio.objects.create(
        nombre=f"Comercio {estado}",
        actividad_comercial=actividad,
        beneficio_texto="No publicar",
        estado=estado,
    )

    response = client.get(reverse("web:comercio_detalle_modal", args=[comercio.pk]))

    assert response.status_code == 404


@pytest.mark.django_db
def test_modal_comercio_inexistente_responde_404(client):
    response = client.get(reverse("web:comercio_detalle_modal", args=[999999]))

    assert response.status_code == 404
