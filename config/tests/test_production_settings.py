import json
import os
import subprocess
import sys


def load_production_settings(**variables):
    environment = os.environ.copy()
    for name in (
        "ALLOWED_HOSTS",
        "CSRF_TRUSTED_ORIGINS",
        "DEBUG",
        "GOOGLE_ANALYTICS_MEASUREMENT_ID",
        "VERCEL_BRANCH_URL",
        "VERCEL_PROJECT_PRODUCTION_URL",
        "VERCEL_URL",
        "UNI2_PRIVATE_DATA_EPOCH",
    ):
        environment.pop(name, None)
    for name in tuple(environment):
        if name.startswith("AWS_"):
            environment.pop(name)

    environment.update(
        {
            "DATABASE_URL": "sqlite:///:memory:",
            "SECRET_KEY": "test-secret-key",
            **variables,
        }
    )
    script = """
import json
from config.settings import production

print(json.dumps({
    "allowed_hosts": production.ALLOWED_HOSTS,
    "analytics_measurement_id": production.GOOGLE_ANALYTICS_MEASUREMENT_ID,
    "csrf_cookie_secure": production.CSRF_COOKIE_SECURE,
    "csrf_trusted_origins": production.CSRF_TRUSTED_ORIGINS,
    "debug": production.DEBUG,
    "hsts_seconds": production.SECURE_HSTS_SECONDS,
    "deployment_environment": production.UNI2_DEPLOYMENT_ENVIRONMENT,
    "private_data_epoch": production.PWA_PRIVATE_DATA_EPOCH,
    "secure_ssl_redirect": production.SECURE_SSL_REDIRECT,
    "session_cookie_secure": production.SESSION_COOKIE_SECURE,
    "storages": production.STORAGES,
    "uses_legacy_staticfiles_storage": hasattr(production, "STATICFILES_STORAGE"),
}))
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        capture_output=True,
        env=environment,
        text=True,
    )
    return json.loads(result.stdout)


def test_produccion_lee_el_identificador_de_google_analytics():
    production = load_production_settings(
        GOOGLE_ANALYTICS_MEASUREMENT_ID=" G-TEST123 "
    )

    assert production["analytics_measurement_id"] == "G-TEST123"


def test_produccion_no_permite_activar_debug_desde_el_entorno():
    production = load_production_settings(DEBUG="True")

    assert production["debug"] is False
    assert production["deployment_environment"] == "production"
    assert production["private_data_epoch"] == "production"
    assert production["secure_ssl_redirect"] is True
    assert production["session_cookie_secure"] is True
    assert production["csrf_cookie_secure"] is True
    assert production["hsts_seconds"] == 3600
    assert production["storages"]["default"]["BACKEND"] == "django.core.files.storage.FileSystemStorage"
    assert production["storages"]["staticfiles"]["BACKEND"] == (
        "whitenoise.storage.CompressedManifestStaticFilesStorage"
    )
    assert production["uses_legacy_staticfiles_storage"] is False


def test_produccion_admite_hosts_configurados_y_urls_exactas_de_vercel():
    production = load_production_settings(
        ALLOWED_HOSTS=" mutual.example ,api.mutual.example,mutual.example",
        CSRF_TRUSTED_ORIGINS=" https://mutual.example ",
        VERCEL_URL="uni2-deploy.vercel.app",
        VERCEL_BRANCH_URL="uni2-main.vercel.app",
        VERCEL_PROJECT_PRODUCTION_URL="mutual.example",
    )

    assert production["allowed_hosts"] == [
        "mutual.example",
        "api.mutual.example",
        "uni2-deploy.vercel.app",
        "uni2-main.vercel.app",
    ]
    assert production["csrf_trusted_origins"] == [
        "https://mutual.example",
        "https://uni2-deploy.vercel.app",
        "https://uni2-main.vercel.app",
    ]


def test_produccion_usa_s3_para_media_sin_cambiar_el_storage_de_estaticos():
    production = load_production_settings(
        AWS_ACCESS_KEY_ID="test-access-key",
        AWS_SECRET_ACCESS_KEY="test-secret-key",
        AWS_STORAGE_BUCKET_NAME="test-bucket",
    )

    assert production["storages"]["default"]["BACKEND"] == "storages.backends.s3.S3Storage"
    assert production["storages"]["staticfiles"]["BACKEND"] == (
        "whitenoise.storage.CompressedManifestStaticFilesStorage"
    )
