import json
import os
import subprocess
import sys


def run_production_settings(**variables):
    environment = os.environ.copy()
    for name in (
        "ALLOWED_HOSTS",
        "CSRF_TRUSTED_ORIGINS",
        "DEBUG",
        "GOOGLE_ANALYTICS_MEASUREMENT_ID",
        "VERCEL_BRANCH_URL",
        "VERCEL_PROJECT_PRODUCTION_URL",
        "VERCEL_URL",
        "VERCEL",
        "UNI2_PRIVATE_DATA_EPOCH",
        "UNI2_SITE_URL",
        "UNI2_TRANSACTIONAL_EMAIL_MODE",
        "DEFAULT_FROM_EMAIL",
        "EMAIL_HOST",
        "EMAIL_PORT",
        "EMAIL_HOST_USER",
        "EMAIL_HOST_PASSWORD",
        "EMAIL_USE_TLS",
    ):
        environment.pop(name, None)
    for name in tuple(environment):
        if name.startswith("AWS_"):
            environment.pop(name)

    environment.update(
        {
            "DATABASE_URL": "sqlite:///:memory:",
            "SECRET_KEY": "test-secret-key",
            "UNI2_TRANSACTIONAL_EMAIL_MODE": "disabled",
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
    "email_backend": getattr(production, "EMAIL_BACKEND", ""),
    "email_host": getattr(production, "EMAIL_HOST", ""),
    "email_port": getattr(production, "EMAIL_PORT", 0),
    "email_use_tls": getattr(production, "EMAIL_USE_TLS", False),
    "from_email": production.DEFAULT_FROM_EMAIL,
    "private_data_epoch": production.PWA_PRIVATE_DATA_EPOCH,
    "secure_ssl_redirect": production.SECURE_SSL_REDIRECT,
    "session_cookie_secure": production.SESSION_COOKIE_SECURE,
    "storages": production.STORAGES,
    "site_url": production.UNI2_SITE_URL,
    "transactional_email_mode": production.UNI2_TRANSACTIONAL_EMAIL_MODE,
    "trust_vercel_client_ip": production.UNI2_TRUST_VERCEL_CLIENT_IP,
    "uses_legacy_staticfiles_storage": hasattr(production, "STATICFILES_STORAGE"),
}))
"""
    return subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        env=environment,
        text=True,
    )


def load_production_settings(**variables):
    result = run_production_settings(**variables)
    result.check_returncode()
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
    assert production["trust_vercel_client_ip"] is False


def test_produccion_confia_en_el_encabezado_de_ip_solo_dentro_de_vercel():
    production = load_production_settings(VERCEL="1")

    assert production["trust_vercel_client_ip"] is True


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


def test_produccion_rechaza_correo_habilitado_sin_configuracion():
    result = run_production_settings(UNI2_TRANSACTIONAL_EMAIL_MODE="enabled")

    assert result.returncode != 0
    assert "EMAIL_HOST" in result.stderr


def test_produccion_configura_smtp_cuando_el_correo_esta_habilitado():
    production = load_production_settings(
        UNI2_TRANSACTIONAL_EMAIL_MODE="enabled",
        UNI2_SITE_URL="https://uni2.example",
        DEFAULT_FROM_EMAIL="UNI2 <no-responder@uni2.example>",
        EMAIL_HOST="smtp.example",
        EMAIL_PORT="587",
        EMAIL_HOST_USER="uni2",
        EMAIL_HOST_PASSWORD="secret-for-tests",
        EMAIL_USE_TLS="true",
    )

    assert production["transactional_email_mode"] == "enabled"
    assert production["site_url"] == "https://uni2.example"
    assert production["from_email"] == "UNI2 <no-responder@uni2.example>"
    assert production["email_backend"] == "django.core.mail.backends.smtp.EmailBackend"
    assert production["email_host"] == "smtp.example"
    assert production["email_port"] == 587
    assert production["email_use_tls"] is True
