from html.parser import HTMLParser
from pathlib import Path

import pytest
from django.contrib.staticfiles import finders
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
    assert content.count('src="/static/js/uni2-actions.js"') == 1
    assert content.index('src="/static/js/uni2-actions.js"') < content.index('src="/static/pwa/uni2-pwa.js"')
    assert "/static/js/uni2-section-navigation.js" in content
    assert 'id="uni2-connectivity-status"' in content
    assert 'id="uni2-install-promotion"' in content
    assert "Instalá UNI2" in content
    assert "data-pwa-install-dismiss" in content
    assert "data-pwa-browser-install-instructions" in content
    assert 'id="uni2-update-banner"' in content
    assert 'class="btn btn-primary" id="uni2-update-apply"' in content
    assert "cdn.jsdelivr.net" not in content
    assert "fonts.googleapis.com" not in content
    assert "fonts.gstatic.com" not in content


def test_navegacion_mobile_cierra_el_menu_antes_de_ir_a_la_seccion():
    script_path = finders.find("js/uni2-section-navigation.js")
    assert script_path is not None
    source = Path(script_path).read_text(encoding="utf-8")

    assert 'menu.classList.contains("show")' in source
    assert '"hidden.bs.collapse"' in source
    assert "Collapse.getOrCreateInstance(menu).hide()" in source
    assert "target.scrollIntoView" in source
    assert 'behavior: "smooth"' not in source


def test_instalacion_ofrece_accion_visible_y_fallback_manual():
    script_path = finders.find("pwa/uni2-pwa.js")
    assert script_path is not None
    source = Path(script_path).read_text(encoding="utf-8")

    assert "if (!isStandalone()) showInstallItems();" in source
    assert "showInstallInstructions();" in source
    assert "choice.outcome === 'accepted'" in source
    assert "data-pwa-install-dismiss" in source
    assert "window.sessionStorage.setItem(INSTALL_PROMOTION_DISMISSED_KEY, 'true')" in source


@pytest.mark.django_db
@override_settings(PWA_CREDENTIAL_OFFLINE_TTL_DAYS=3)
def test_base_expone_el_ttl_configurado_sin_duplicarlo_en_javascript(client):
    content = client.get(reverse("web:home")).content.decode()

    assert 'data-pwa-credential-ttl-days="3"' in content


@pytest.mark.django_db
@override_settings(
    PWA_APP_NAME="UNI2 - Entorno de prueba",
    PWA_SHORT_NAME="UNI2 STG",
    PWA_PRIVATE_DATA_EPOCH="2026-08-02-01",
    PWA_THEME_COLOR_LIGHT="#fff4e8",
    PWA_THEME_COLOR_DARK="#2a1208",
    PWA_ICON_DIRECTORY="pwa/icons/staging",
    UNI2_DEPLOYMENT_ENVIRONMENT="staging",
    UNI2_ENVIRONMENT_LABEL="STAGING · DATOS REALES",
    UNI2_ENVIRONMENT_SHORT_LABEL="STAGING",
)
def test_base_identifica_staging_y_expone_epoch_para_datos_privados(client):
    content = client.get(reverse("web:home")).content.decode()

    assert 'data-deployment-environment="staging"' in content
    assert "STAGING · DATOS REALES" in content
    assert 'class="uni2-environment-badge">STAGING</span>' in content
    assert "<title>Inicio | Uni2 · STAGING</title>" in content
    assert 'content="UNI2 STG"' in content
    assert 'data-pwa-private-data-epoch="2026-08-02-01"' in content
    assert 'data-pwa-theme-color-light="#fff4e8"' in content
    assert 'data-pwa-theme-color-dark="#2a1208"' in content
    assert 'data-pwa-short-name="UNI2 STG"' in content
    assert "/static/pwa/icons/staging/favicon-32.png" in content
    assert "/static/pwa/icons/staging/icon-192.png" in content
    assert "/static/pwa/icons/staging/apple-touch-icon-180.png" in content


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
        "data-credential-dato-etiqueta",
        "data-credential-dato-valor",
        "data-credential-estado",
        "data-credential-token",
        "data-credential-url",
    }
    assert (
        credential_attrs["data-credential-url"]
        == f"http://testserver/credenciales/{asociado.token_credencial}/"
    )
    assert (
        f'data-uni2-qr-value="http://testserver/credenciales/{asociado.token_credencial}/"'
        in content
    )
    assert asociado.dni in content
    assert "data-credential-dni" not in content
    assert asociado.email not in content
    assert asociado.telefono not in content
    assert asociado.direccion not in content
    assert "data-credential-deuda" not in content
    assert 'id="uni2-credential-save"' in content
    assert 'id="uni2-credential-delete"' in content
    assert "durante 7 días" in content


def test_copia_offline_conserva_la_url_del_qr_y_admite_registros_anteriores():
    credential_script = Path(finders.find("pwa/uni2-credential.js")).read_text(encoding="utf-8")
    storage_script = Path(finders.find("pwa/uni2-private-storage.js")).read_text(encoding="utf-8")

    assert "credentialUrl: root.dataset.credentialUrl" in credential_script
    assert "credential.credentialUrl ||" in credential_script
    assert "credentialUrl: String(credential.credentialUrl)" in storage_script


def test_copia_offline_interpreta_activa_como_estado_vigente():
    credential_script = Path(finders.find("pwa/uni2-credential.js")).read_text(encoding="utf-8")

    assert "credential.ultimoEstado.trim().toLowerCase() === 'activa'" in credential_script
    assert "credential.ultimoEstado.trim().toLowerCase() === 'activo'" not in credential_script


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

    content = client.get(reverse("web:home")).content.decode()

    assert content.count("data-pwa-logout") >= 2
