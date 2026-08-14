from pathlib import Path

import pytest
from django.urls import reverse
from django.contrib.staticfiles import finders

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


@pytest.mark.django_db
def test_listado_conserva_href_completo_y_declara_endpoint_modal(
    client, actividad, comercio_firmado
):
    response = client.get(
        reverse("web:actividad_comercial_detalle", args=[actividad.pk])
    )

    content = response.content.decode()
    full_url = reverse("web:comercio_detalle", args=[comercio_firmado.pk])
    modal_url = reverse("web:comercio_detalle_modal", args=[comercio_firmado.pk])
    assert f'href="{full_url}"' in content
    assert f'data-commerce-modal-url="{modal_url}"' in content
    assert 'class="uni2-benefit-detail-link js-commerce-modal-link"' in content
    assert content.count(" data-commerce-modal>") == 1
    assert content.count(" data-commerce-modal-content>") == 1
    assert "js/uni2-commerce-modal.js" in content


def test_script_modal_de_comercios_existe_en_staticfiles():
    assert finders.find("js/uni2-commerce-modal.js") is not None


def test_script_modal_aborta_la_solicitud_al_comenzar_el_cierre():
    script_path = finders.find("js/uni2-commerce-modal.js")

    script = Path(script_path).read_text()

    assert 'modalElement.addEventListener("hide.bs.modal", function () {' in script
    assert "if (activeRequest) activeRequest.abort();" in script
