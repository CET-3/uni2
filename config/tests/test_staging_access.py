import base64
import json

import pytest
from django.http import HttpResponse
from django.test import RequestFactory, override_settings
from django.urls import reverse
from django.utils import timezone

from config.middleware import StagingAccessMiddleware
from config.views import staging_readiness
from usuarios.models import EstadoDatosStaging


def basic_auth(username, password):
    encoded = base64.b64encode(f"{username}:{password}".encode()).decode()
    return f"Basic {encoded}"


@override_settings(
    UNI2_STAGING_ACCESS_USERNAME="qa",
    UNI2_STAGING_ACCESS_PASSWORD="clave-separada",
)
def test_staging_rechaza_pedidos_sin_credenciales_y_no_los_indexa():
    middleware = StagingAccessMiddleware(lambda request: HttpResponse("privado"))
    response = middleware(RequestFactory().get("/"))

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"].startswith('Basic realm="UNI2 Staging"')
    assert response.headers["Cache-Control"] == "private, no-store"
    assert response.headers["X-Robots-Tag"] == "noindex, nofollow, noarchive"
    assert b"privado" not in response.content


@pytest.mark.parametrize(
    "path",
    [
        "/manifest.webmanifest",
        "/service-worker.js",
        "/sin-conexion/",
        "/sin-conexion/accion-no-enviada/",
        "/sin-conexion/credencial/",
        "/static/pwa/icons/staging/icon-192.png",
    ],
)
def test_staging_deja_disponible_solo_el_shell_pwa_neutro_sin_credenciales(path):
    middleware = StagingAccessMiddleware(lambda request: HttpResponse("recurso PWA"))

    response = middleware(RequestFactory().get(path))

    assert response.status_code == 200
    assert response.content == b"recurso PWA"
    assert response.headers["Cache-Control"] == "private, no-store"
    assert response.headers["X-Robots-Tag"] == "noindex, nofollow, noarchive"


@pytest.mark.parametrize(
    "path",
    [
        "/",
        "/media/comercios/foto.jpg",
        "/service-worker.js/otro",
        "/sin-conexion/privado/",
    ],
)
@override_settings(
    UNI2_STAGING_ACCESS_USERNAME="qa",
    UNI2_STAGING_ACCESS_PASSWORD="clave-separada",
)
def test_staging_no_extiende_la_excepcion_pwa_a_otras_rutas(path):
    middleware = StagingAccessMiddleware(lambda request: HttpResponse("privado"))

    response = middleware(RequestFactory().get(path))

    assert response.status_code == 401
    assert b"privado" not in response.content


@override_settings(
    UNI2_STAGING_ACCESS_USERNAME="qa",
    UNI2_STAGING_ACCESS_PASSWORD="clave-separada",
)
def test_staging_no_hace_publicas_mutaciones_sobre_rutas_pwa():
    middleware = StagingAccessMiddleware(lambda request: HttpResponse("mutacion"))

    response = middleware(RequestFactory().post(reverse("pwa:manifest")))

    assert response.status_code == 401
    assert b"mutacion" not in response.content


@override_settings(
    UNI2_STAGING_ACCESS_USERNAME="qa",
    UNI2_STAGING_ACCESS_PASSWORD="clave-separada",
    PWA_PRIVATE_DATA_EPOCH="2026-08-02-01",
)
@pytest.mark.django_db
def test_staging_admite_credenciales_correctas_y_mantiene_noindex():
    EstadoDatosStaging.objects.create(
        refresh_id="2026-08-02-01",
        listo_desde=timezone.now(),
    )
    middleware = StagingAccessMiddleware(lambda request: HttpResponse("contenido"))
    request = RequestFactory().get("/", HTTP_AUTHORIZATION=basic_auth("qa", "clave-separada"))
    response = middleware(request)

    assert response.status_code == 200
    assert response.content == b"contenido"
    assert response.headers["Cache-Control"] == "private, no-store"
    assert response.headers["X-Robots-Tag"] == "noindex, nofollow, noarchive"
    assert "Authorization" in response.headers["Vary"]


@override_settings(
    UNI2_STAGING_ACCESS_USERNAME="qa",
    UNI2_STAGING_ACCESS_PASSWORD="clave-separada",
)
def test_staging_rechaza_basic_auth_malformado():
    middleware = StagingAccessMiddleware(lambda request: HttpResponse("privado"))
    request = RequestFactory().get("/", HTTP_AUTHORIZATION="Basic no-es-base64")

    assert middleware(request).status_code == 401


@override_settings(
    UNI2_STAGING_ACCESS_USERNAME="qa",
    UNI2_STAGING_ACCESS_PASSWORD="clave-separada",
    PWA_PRIVATE_DATA_EPOCH="2026-08-02-02",
)
@pytest.mark.django_db
def test_staging_no_sirve_una_copia_sin_marcador_del_epoch_actual():
    EstadoDatosStaging.objects.create(
        refresh_id="2026-08-02-01",
        listo_desde=timezone.now(),
    )
    middleware = StagingAccessMiddleware(lambda request: HttpResponse("contenido"))
    request = RequestFactory().get("/", HTTP_AUTHORIZATION=basic_auth("qa", "clave-separada"))

    response = middleware(request)

    assert response.status_code == 503
    assert response.headers["Retry-After"] == "60"
    assert response.headers["Cache-Control"] == "private, no-store"
    assert b"contenido" not in response.content


@override_settings(
    UNI2_DEPLOYMENT_ENVIRONMENT="staging",
    PWA_BUILD_ID="commit-staging",
)
@pytest.mark.django_db
def test_readiness_informa_build_epoch_y_migraciones_sin_datos_personales():
    state = EstadoDatosStaging(
        refresh_id="2026-08-02-01",
        listo_desde=timezone.now(),
    )
    request = RequestFactory().get("/__staging__/readiness/")
    request.uni2_staging_data_state = state

    response = staging_readiness(request)

    assert response.status_code == 200
    assert response.content == (
        b'{"build_id": "commit-staging", "data_epoch": "2026-08-02-01", '
        b'"environment": "staging", "migrations_current": true, '
        b'"pending_migrations": [], "ready": true}'
    )


@override_settings(
    UNI2_DEPLOYMENT_ENVIRONMENT="staging",
    PWA_BUILD_ID="commit-staging",
)
def test_readiness_rechaza_un_esquema_con_migraciones_pendientes(monkeypatch):
    monkeypatch.setattr(
        "config.views._pending_migration_names",
        lambda: ["contenidos.0008_alter_categoriaproductoservicio_etiqueta_icono"],
    )
    request = RequestFactory().get("/__staging__/readiness/")
    request.uni2_staging_data_state = EstadoDatosStaging(
        refresh_id="2026-08-02-01",
        listo_desde=timezone.now(),
    )

    response = staging_readiness(request)

    assert response.status_code == 503
    payload = json.loads(response.content)
    assert payload["migrations_current"] is False
    assert payload["ready"] is False
    assert payload["pending_migrations"] == [
        "contenidos.0008_alter_categoriaproductoservicio_etiqueta_icono"
    ]
    assert payload["reason"] == "migrations_pending"
