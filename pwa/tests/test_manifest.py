from pathlib import Path

from django.contrib.staticfiles import finders
from django.test import override_settings
from django.urls import resolve, reverse
from PIL import Image


def test_ruta_del_manifest_es_estable():
    assert reverse("pwa:manifest") == "/manifest.webmanifest"
    assert resolve("/manifest.webmanifest").view_name == "pwa:manifest"


def test_manifest_declara_identidad_y_scope_de_uni2(client):
    response = client.get(reverse("pwa:manifest"))

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/manifest+json"
    assert response.headers["Cache-Control"] == "no-cache, max-age=0, must-revalidate"

    manifest = response.json()
    assert manifest["id"] == "/"
    assert manifest["name"] == "UNI2 - Mutual Escolar"
    assert manifest["short_name"] == "UNI2"
    assert manifest["lang"] == "es-AR"
    assert manifest["dir"] == "ltr"
    assert manifest["start_url"] == "/"
    assert manifest["scope"] == "/"
    assert manifest["display"] == "standalone"
    assert manifest["prefer_related_applications"] is False
    assert manifest["theme_color"] == "#3f51b5"
    assert manifest["background_color"] == "#f7f9fc"


def test_manifest_declara_iconos_normales_y_maskable_existentes(client):
    response = client.get(reverse("pwa:manifest"))
    icons = response.json()["icons"]

    expected = {
        "/static/pwa/icons/icon-192.png": ("192x192", "any", (192, 192)),
        "/static/pwa/icons/icon-512.png": ("512x512", "any", (512, 512)),
        "/static/pwa/icons/icon-maskable-192.png": ("192x192", "maskable", (192, 192)),
        "/static/pwa/icons/icon-maskable-512.png": ("512x512", "maskable", (512, 512)),
    }

    assert {icon["src"] for icon in icons} == set(expected)
    for icon in icons:
        sizes, purpose, dimensions = expected[icon["src"]]
        assert icon == {
            "src": icon["src"],
            "sizes": sizes,
            "type": "image/png",
            "purpose": purpose,
        }
        static_path = icon["src"].removeprefix("/static/")
        found_path = finders.find(static_path)
        assert found_path is not None, static_path
        assert Path(found_path).is_file()
        with Image.open(found_path) as image:
            assert image.size == dimensions
            assert image.format == "PNG"


def test_manifest_ofrece_accesos_directos_internos(client):
    shortcuts = client.get(reverse("pwa:manifest")).json()["shortcuts"]

    assert {shortcut["url"] for shortcut in shortcuts} == {
        reverse("web:productos_servicios"),
        reverse("web:comercios"),
        reverse("usuarios:login"),
    }
    assert all(shortcut["url"].startswith("/") for shortcut in shortcuts)


def test_manifest_solo_admite_get(client):
    response = client.post(reverse("pwa:manifest"))

    assert response.status_code == 405


@override_settings(
    PWA_APP_NAME="UNI2 - Entorno de prueba",
    PWA_SHORT_NAME="UNI2 STG",
    PWA_DESCRIPTION="Entorno protegido de prueba.",
    PWA_THEME_COLOR="#a83a00",
    PWA_BACKGROUND_COLOR="#fff4e8",
    PWA_ICON_DIRECTORY="pwa/icons/staging",
)
def test_manifest_distingue_staging_sin_cambiar_la_identidad_por_origen(client):
    manifest = client.get(reverse("pwa:manifest")).json()

    assert manifest["id"] == "/"
    assert manifest["name"] == "UNI2 - Entorno de prueba"
    assert manifest["short_name"] == "UNI2 STG"
    assert manifest["description"] == "Entorno protegido de prueba."
    assert manifest["theme_color"] == "#a83a00"
    assert manifest["background_color"] == "#fff4e8"
    assert {icon["src"] for icon in manifest["icons"]} == {
        "/static/pwa/icons/staging/icon-192.png",
        "/static/pwa/icons/staging/icon-512.png",
        "/static/pwa/icons/staging/icon-maskable-192.png",
        "/static/pwa/icons/staging/icon-maskable-512.png",
    }
    for icon in manifest["icons"]:
        found_path = finders.find(icon["src"].removeprefix("/static/"))
        assert found_path is not None
        with Image.open(found_path) as image:
            assert image.size == tuple(int(value) for value in icon["sizes"].split("x"))
