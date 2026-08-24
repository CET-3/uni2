from pathlib import Path
import re
from html.parser import HTMLParser

import pytest
from django.urls import reverse
from django.contrib.staticfiles import finders

from comercios.models import ActividadComercial, Comercio


class ElementParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = []
        self.ancestors = []
        self._open_elements = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        self.elements.append((tag, attributes))
        self.ancestors.append(tuple(self._open_elements))
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}:
            self._open_elements.append((tag, attributes))

    def handle_endtag(self, tag):
        for index in range(len(self._open_elements) - 1, -1, -1):
            if self._open_elements[index][0] == tag:
                del self._open_elements[index:]
                break

    def elements_with(self, **attributes):
        return [
            (tag, attrs)
            for tag, attrs in self.elements
            if all(
                name in attrs and attrs[name] == value
                for name, value in attributes.items()
            )
        ]

    def elements_with_class(self, class_name):
        return [
            (tag, attrs)
            for tag, attrs in self.elements
            if class_name in attrs.get("class", "").split()
        ]


def parse_html(content):
    parser = ElementParser()
    parser.feed(content)
    return parser


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

    partial = parse_html(content)
    assert partial.elements_with_class("modal-header") == []
    assert partial.elements_with_class("modal-body") == []
    assert partial.elements_with_class("btn-close") == []
    assert partial.elements_with(id="comercio-modal-title")
    assert len(partial.elements_with_class("uni2-commerce-modal-card")) == 1
    assert len(partial.elements_with_class("uni2-commerce-modal-logo")) == 1
    assert len(partial.elements_with_class("uni2-commerce-modal-benefit")) == 1
    assert len(partial.elements_with_class("uni2-commerce-modal-meta")) == 1
    assert len(partial.elements_with_class("uni2-commerce-modal-actions")) == 1
    assert partial.elements_with_class("uni2-detail-layout") == []


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

    page = parse_html(response.content.decode())
    full_url = reverse("web:comercio_detalle", args=[comercio_firmado.pk])
    modal_url = reverse("web:comercio_detalle_modal", args=[comercio_firmado.pk])
    links = [
        attrs
        for tag, attrs in page.elements
        if tag == "a" and attrs.get("href") == full_url
    ]

    assert len(links) == 1
    assert {"uni2-benefit-detail-link", "js-commerce-modal-link"} <= set(
        links[0]["class"].split()
    )
    assert links[0]["data-commerce-modal-url"] == modal_url
    modal_elements = page.elements_with(**{"data-commerce-modal": None})
    assert len(modal_elements) == 1
    modal_classes = set(modal_elements[0][1]["class"].split())
    assert {"modal", "uni2-commerce-modal"} <= modal_classes
    assert "fade" not in modal_classes
    assert len(page.elements_with(**{"data-commerce-modal-content": None})) == 1
    assert len(page.elements_with(id="comercio-modal-title")) == 1

    dialogs = [
        (tag, attrs)
        for (tag, attrs), ancestors in zip(page.elements, page.ancestors)
        if "modal-dialog" in attrs.get("class", "").split()
        and any("data-commerce-modal" in ancestor_attrs for _, ancestor_attrs in ancestors)
    ]
    assert len(dialogs) == 1
    assert "modal-dialog-scrollable" in dialogs[0][1]["class"].split()
    assert "uni2-commerce-modal-dialog" in dialogs[0][1]["class"].split()
    assert "modal-lg" not in dialogs[0][1]["class"].split()

    close_buttons = [
        attrs
        for (tag, attrs), ancestors in zip(page.elements, page.ancestors)
        if tag == "button"
        and "btn-close" in attrs.get("class", "").split()
        and any("data-commerce-modal" in ancestor_attrs for _, ancestor_attrs in ancestors)
    ]
    assert len(close_buttons) == 1
    assert close_buttons[0]["data-bs-dismiss"] == "modal"
    assert close_buttons[0]["aria-label"] == "Cerrar"


def test_script_modal_de_comercios_existe_en_staticfiles():
    assert finders.find("js/uni2-commerce-modal.js") is not None


def test_script_modal_aborta_la_solicitud_al_comenzar_el_cierre():
    script_path = finders.find("js/uni2-commerce-modal.js")

    script = Path(script_path).read_text()

    listener = re.search(
        r'modalElement\.addEventListener\("hide\.bs\.modal", function \(\) \{(?P<body>.*?)\n    \}\);',
        script,
        re.DOTALL,
    )

    assert listener is not None
    assert "activeRequest.abort()" in listener.group("body")


def test_estados_de_carga_y_error_conservan_el_titulo_del_modal():
    script_path = finders.find("js/uni2-commerce-modal.js")

    script = Path(script_path).read_text()

    loading = re.search(
        r"function renderLoading\(\) \{(?P<body>.*?)\n    \}", script, re.DOTALL
    )
    error = re.search(
        r"function renderError\(fullUrl\) \{(?P<body>.*?)\n    \}",
        script,
        re.DOTALL,
    )

    assert loading is not None
    assert error is not None
    assert 'id="comercio-modal-title"' in loading.group("body")
    assert 'title.id = "comercio-modal-title"' in error.group("body")


def test_css_modal_define_presentacion_compacta_propia():
    css_path = finders.find("css/uni2-design-system.css")

    css = Path(css_path).read_text()

    assert ".uni2-commerce-modal-dialog" in css
    assert ".uni2-commerce-modal-card" in css
    assert ".uni2-commerce-modal-logo" in css
    assert ".uni2-commerce-modal-benefit" in css
    assert ".uni2-commerce-modal-meta" in css
