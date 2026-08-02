from html.parser import HTMLParser

import pytest
from django.test import override_settings
from django.urls import reverse

from asociados.services import create_asociado


class TagByIdParser(HTMLParser):
    def __init__(self, element_id):
        super().__init__()
        self.element_id = element_id
        self.attrs = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if attributes.get("id") == self.element_id:
            self.attrs = attributes


def attrs_for_id(content, element_id):
    parser = TagByIdParser(element_id)
    parser.feed(content)
    assert parser.attrs is not None, element_id
    return parser.attrs


@pytest.mark.django_db
def test_base_integra_manifest_worker_y_componentes_pwa(client):
    content = client.get(reverse("web:home")).content.decode()

    assert f'rel="manifest" href="{reverse("pwa:manifest")}"' in content
    assert "/static/pwa/icons/apple-touch-icon-180.png" in content
    assert "/static/pwa/uni2-private-storage.js" in content
    assert "/static/pwa/uni2-pwa.js" in content
    assert 'id="uni2-connectivity-status"' in content
    assert 'id="uni2-update-banner"' in content
    assert 'class="btn btn-primary" id="uni2-update-apply"' in content
    assert "cdn.jsdelivr.net" not in content
    assert "fonts.googleapis.com" not in content
    assert "fonts.gstatic.com" not in content


@pytest.mark.django_db
@override_settings(PWA_CREDENTIAL_OFFLINE_TTL_DAYS=3)
def test_base_expone_el_ttl_configurado_sin_duplicarlo_en_javascript(client):
    content = client.get(reverse("web:home")).content.decode()

    assert 'data-pwa-credential-ttl-days="3"' in content


@pytest.mark.django_db
def test_credencial_solo_expone_al_cliente_campos_offline_permitidos(client):
    asociado = create_asociado(
        nombre="Nora",
        apellido="Privacidad",
        dni="40777666",
        tipo="asociado",
        fecha_alta="2026-07-01",
        email="nora-privada@example.test",
        telefono="2994445555",
        direccion="Calle privada 456",
    )
    client.force_login(asociado.usuario)

    content = client.get(reverse("asociados:credencial")).content.decode()
    credential_attrs = attrs_for_id(content, "uni2-credential")
    offline_attr_names = {
        name for name in credential_attrs if name.startswith("data-credential-")
    }

    assert offline_attr_names == {
        "data-credential-nombre",
        "data-credential-apellido",
        "data-credential-numero",
        "data-credential-tipo",
        "data-credential-estado",
        "data-credential-token",
    }
    assert asociado.dni not in content
    assert asociado.email not in content
    assert asociado.telefono not in content
    assert asociado.direccion not in content
    assert "data-credential-deuda" not in content
    assert 'id="uni2-credential-save"' in content
    assert 'id="uni2-credential-delete"' in content
    assert "durante 7 días" in content


@pytest.mark.django_db
def test_logout_esta_marcado_para_limpiar_credencial_privada(client):
    asociado = create_asociado(
        nombre="Luz",
        apellido="Logout",
        dni="40666555",
        tipo="asociado",
        fecha_alta="2026-07-01",
    )
    client.force_login(asociado.usuario)

    content = client.get(reverse("asociados:dashboard")).content.decode()

    assert content.count("data-pwa-logout") >= 2
