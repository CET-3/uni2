import json

from django.test import override_settings
from django.urls import resolve, reverse


def test_ruta_del_service_worker_es_raiz_y_estable():
    assert reverse("pwa:service_worker") == "/service-worker.js"
    assert resolve("/service-worker.js").view_name == "pwa:service_worker"


@override_settings(
    PWA_BUILD_ID="release/2026 08 01",
    PWA_PRIVATE_DATA_EPOCH="refresh/2026 08 02",
)
def test_worker_declara_scope_headers_y_build_normalizado(client):
    response = client.get(reverse("pwa:service_worker"))
    source = response.content.decode()

    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/javascript")
    assert response.headers["Service-Worker-Allowed"] == "/"
    assert response.headers["Cache-Control"] == "no-cache, max-age=0, must-revalidate"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert "Vary" not in response.headers
    assert 'const BUILD_ID = "release-2026-08-01";' in source
    assert 'const DATA_EPOCH = "refresh-2026-08-02";' in source
    assert "const CACHE_VERSION = `${BUILD_ID}-${DATA_EPOCH}`;" in source


@override_settings(PWA_ICON_DIRECTORY="pwa/icons/staging")
def test_worker_precachea_los_iconos_exclusivos_de_staging(client):
    source = client.get(reverse("pwa:service_worker")).content.decode()

    assert "/static/pwa/icons/staging/icon-192.png" in source
    assert "/static/pwa/icons/staging/icon-512.png" in source
    assert "/static/pwa/icons/icon-192.png" not in source


def test_worker_precachea_shell_y_assets_locales(client):
    source = client.get(reverse("pwa:service_worker")).content.decode()

    marker = "const PRECACHE_URLS = JSON.parse("
    assert marker in source
    assert reverse("pwa:offline") in source
    assert reverse("pwa:offline_action") in source
    assert reverse("pwa:offline_credential") in source
    assert "/static/vendor/bootstrap/5.3.3/css/bootstrap.min.css" in source
    assert "/static/vendor/bootstrap/5.3.3/js/bootstrap.bundle.min.js" in source
    assert "/static/pwa/uni2-pwa.js" in source
    assert "/static/pwa/uni2-private-storage.js" in source
    assert "/static/pwa/uni2-credential.js" in source

    # El JSON inyectado debe seguir siendo válido antes de que el template lo
    # convierta en una cadena JavaScript.
    response_source = source.split(marker, 1)[1].split(");", 1)[0]
    encoded_json = json.loads(response_source)
    precache_urls = json.loads(encoded_json)
    assert len(precache_urls) == len(set(precache_urls))


@override_settings(UNI2_DEPLOYMENT_ENVIRONMENT="production")
def test_worker_productivo_solo_activa_version_nueva_por_mensaje_explicito(client):
    source = client.get(reverse("pwa:service_worker")).content.decode()

    assert "const DEVELOPMENT_MODE = false;" in source
    assert 'event.data.type === "SKIP_WAITING"' in source
    install_block = source.split('self.addEventListener("install"', 1)[1].split(
        'self.addEventListener("activate"', 1
    )[0]
    assert "event.waitUntil(DEVELOPMENT_MODE ?" in install_block


@override_settings(UNI2_DEPLOYMENT_ENVIRONMENT="development")
def test_worker_desarrollo_actualiza_estaticos_desde_la_red(client):
    source = client.get(reverse("pwa:service_worker")).content.decode()

    assert "const DEVELOPMENT_MODE = true;" in source
    assert 'fetch(request, {cache: "no-store"})' in source
    assert "networkFirstStaticInDevelopment(request)" in source
    install_block = source.split('self.addEventListener("install"', 1)[1].split(
        'self.addEventListener("activate"', 1
    )[0]
    assert "self.skipWaiting()" in install_block


def test_worker_no_encola_mutaciones_y_solo_cachea_paginas_marcadas(client):
    source = client.get(reverse("pwa:service_worker")).content.decode()

    assert 'response.headers.get("X-Uni2-PWA-Cacheable") === "public"' in source
    assert 'request.method !== "GET"' in source
    assert "networkOnlyMutation(request)" in source
    assert 'addEventListener("sync"' not in source
    assert "SyncManager" not in source
    assert "indexedDB" not in source
    assert 'addEventListener("push"' not in source
    assert "PushManager" not in source
    assert "Notification.requestPermission" not in source


@override_settings(AWS_S3_CUSTOM_DOMAIN="media.example.test")
def test_worker_limita_cache_de_imagenes_a_media_publica_configurada(client):
    source = client.get(reverse("pwa:service_worker")).content.decode()

    assert 'const PUBLIC_MEDIA_ORIGIN = "https://media.example.test";' in source
    assert 'request.destination === "image"' in source
    assert "isAllowedPublicImage(url)" in source
    assert "const MAX_PUBLIC_IMAGES = 60;" in source
    assert "staleWhileRevalidatePublicImage" in source
    assert 'response.type === "opaque"' in source


def test_worker_solo_admite_get(client):
    response = client.post(reverse("pwa:service_worker"))

    assert response.status_code == 405
