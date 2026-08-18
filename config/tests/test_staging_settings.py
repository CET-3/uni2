import json
import os
import subprocess
import sys

from config.database_identity import (
    database_fingerprint,
    database_role_fingerprint,
    storage_fingerprint,
)


STAGING_DATABASE = {
    "HOST": "staging-db.example.test",
    "PORT": "5432",
    "NAME": "uni2_staging",
    "USER": "staging-user",
}


def load_staging_settings(**overrides):
    environment = os.environ.copy()
    for name in tuple(environment):
        if name.startswith(("AWS_", "UNI2_")) or name == "GOOGLE_ANALYTICS_MEASUREMENT_ID":
            environment.pop(name)

    environment.update(
        {
            "DATABASE_URL": (
                "postgresql://staging-user:test-password@"
                "staging-db.example.test:5432/uni2_staging"
            ),
            "SECRET_KEY": "staging-secret-key-for-tests-123456",
            "UNI2_ENVIRONMENT": "staging",
            "UNI2_PRIVATE_DATA_EPOCH": "2026-08-02-01",
            "UNI2_PRODUCTION_DATABASE_FINGERPRINT": "f" * 64,
            "UNI2_PRODUCTION_DATABASE_ROLE_FINGERPRINT": "e" * 64,
            "UNI2_STAGING_ACCESS_PASSWORD": "http-password-for-tests",
            "UNI2_STAGING_ACCESS_USERNAME": "qa",
            "UNI2_STAGING_DATABASE_FINGERPRINT": database_fingerprint(STAGING_DATABASE),
            "UNI2_STAGING_DATABASE_ROLE_FINGERPRINT": database_role_fingerprint(
                STAGING_DATABASE
            ),
            "UNI2_STAGING_DATABASE_LABEL": "uni2-staging",
            **overrides,
        }
    )
    script = """
import json
from config.settings import staging

print(json.dumps({
    "allow_demo_data": staging.ALLOW_DEMO_DATA,
    "analytics_measurement_id": staging.GOOGLE_ANALYTICS_MEASUREMENT_ID,
    "app_name": staging.PWA_APP_NAME,
    "batch_email_mode": staging.UNI2_BATCH_EMAIL_MODE,
    "build_id": staging.PWA_BUILD_ID,
    "debug": staging.DEBUG,
    "email_backend": staging.EMAIL_BACKEND,
    "environment": staging.UNI2_DEPLOYMENT_ENVIRONMENT,
    "epoch": staging.PWA_PRIVATE_DATA_EPOCH,
    "icon_directory": staging.PWA_ICON_DIRECTORY,
    "middleware": staging.MIDDLEWARE,
    "push_mode": staging.UNI2_WEB_PUSH_MODE,
    "short_name": staging.PWA_SHORT_NAME,
    "storage_backend": staging.STORAGES["default"]["BACKEND"],
    "storage_access_key": staging.AWS_ACCESS_KEY_ID,
    "storage_secret_key": staging.AWS_SECRET_ACCESS_KEY,
    "storage_custom_domain": getattr(staging, "AWS_S3_CUSTOM_DOMAIN", None),
    "storage_querystring_auth": getattr(staging, "AWS_QUERYSTRING_AUTH", None),
    "storages_app_enabled": "storages" in staging.INSTALLED_APPS,
    "transactional_email_mode": staging.UNI2_TRANSACTIONAL_EMAIL_MODE,
}))
"""
    return subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        env=environment,
        text=True,
    )


def test_staging_es_seguro_y_visualmente_distinto():
    result = load_staging_settings(PWA_BUILD_ID="staging-commit")

    assert result.returncode == 0, result.stderr
    staging = json.loads(result.stdout)
    assert staging == {
        "allow_demo_data": False,
        "analytics_measurement_id": "",
        "app_name": "UNI2 - Entorno de prueba",
        "batch_email_mode": "disabled",
        "build_id": "staging-commit",
        "debug": False,
        "email_backend": "django.core.mail.backends.dummy.EmailBackend",
        "environment": "staging",
        "epoch": "2026-08-02-01",
        "icon_directory": "pwa/icons/staging",
        "middleware": [
            "django.middleware.security.SecurityMiddleware",
            "config.middleware.StagingAccessMiddleware",
            "whitenoise.middleware.WhiteNoiseMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "pwa.middleware.PWACacheControlMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
        ],
        "push_mode": "disabled",
        "short_name": "UNI2 STG",
        "storage_backend": "django.core.files.storage.FileSystemStorage",
        "storage_access_key": None,
        "storage_secret_key": None,
        "storage_custom_domain": None,
        "storage_querystring_auth": True,
        "storages_app_enabled": False,
        "transactional_email_mode": "disabled",
    }


def test_staging_no_hereda_google_analytics_de_produccion():
    result = load_staging_settings(GOOGLE_ANALYTICS_MEASUREMENT_ID="G-TEST123")

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["analytics_measurement_id"] == ""


def test_staging_rechaza_una_base_con_huella_productiva():
    fingerprint = database_fingerprint(STAGING_DATABASE)
    result = load_staging_settings(UNI2_PRODUCTION_DATABASE_FINGERPRINT=fingerprint)

    assert result.returncode != 0
    assert "Staging no puede usar la base de Producción" in result.stderr


def test_staging_rechaza_una_huella_declarada_que_no_corresponde():
    result = load_staging_settings(UNI2_STAGING_DATABASE_FINGERPRINT="0" * 64)

    assert result.returncode != 0
    assert "DATABASE_URL no coincide" in result.stderr


def test_staging_rechaza_placeholders_en_huellas_obligatorias():
    for name in (
        "UNI2_STAGING_DATABASE_FINGERPRINT",
        "UNI2_PRODUCTION_DATABASE_FINGERPRINT",
        "UNI2_STAGING_DATABASE_ROLE_FINGERPRINT",
        "UNI2_PRODUCTION_DATABASE_ROLE_FINGERPRINT",
    ):
        result = load_staging_settings(**{name: "reemplazar"})

        assert result.returncode != 0
        assert f"{name} debe ser una huella SHA-256" in result.stderr


def test_staging_rechaza_reutilizar_el_rol_productivo():
    role_fingerprint = database_role_fingerprint(STAGING_DATABASE)
    result = load_staging_settings(
        UNI2_PRODUCTION_DATABASE_ROLE_FINGERPRINT=role_fingerprint
    )

    assert result.returncode != 0
    assert "rol PostgreSQL productivo" in result.stderr


def test_staging_rechaza_una_huella_de_rol_declarada_incorrecta():
    result = load_staging_settings(
        UNI2_STAGING_DATABASE_ROLE_FINGERPRINT="0" * 64,
    )

    assert result.returncode != 0
    assert "rol de DATABASE_URL no coincide" in result.stderr


def test_staging_requiere_barrera_de_acceso():
    result = load_staging_settings(UNI2_STAGING_ACCESS_PASSWORD="")

    assert result.returncode != 0
    assert "UNI2_STAGING_ACCESS_PASSWORD" in result.stderr


def test_staging_rechaza_una_contrasena_http_corta():
    result = load_staging_settings(UNI2_STAGING_ACCESS_PASSWORD="demasiado-corta")

    assert result.returncode != 0
    assert "debe tener al menos 20 caracteres" in result.stderr


def test_staging_rechaza_reutilizar_secret_key_en_la_barrera_http():
    shared_secret = "un-secreto-compartido-muy-inseguro"
    result = load_staging_settings(
        SECRET_KEY=shared_secret,
        UNI2_STAGING_ACCESS_PASSWORD=shared_secret,
    )

    assert result.returncode != 0
    assert "no puede reutilizar SECRET_KEY" in result.stderr


def test_staging_rechaza_sqlite_aunque_la_huella_haya_sido_declarada():
    sqlite_database = {"HOST": "", "PORT": "", "NAME": ":memory:", "USER": ""}
    result = load_staging_settings(
        DATABASE_URL="sqlite:///:memory:",
        UNI2_STAGING_DATABASE_FINGERPRINT=database_fingerprint(sqlite_database),
    )

    assert result.returncode != 0
    assert "Staging requiere una base PostgreSQL separada" in result.stderr


def test_staging_no_hereda_el_bucket_productivo():
    result = load_staging_settings(
        AWS_ACCESS_KEY_ID="production-access",
        AWS_SECRET_ACCESS_KEY="production-secret",
        AWS_STORAGE_BUCKET_NAME="production-bucket",
    )

    assert result.returncode == 0, result.stderr
    staging = json.loads(result.stdout)
    assert staging["storage_backend"] == (
        "django.core.files.storage.FileSystemStorage"
    )
    assert staging["storage_access_key"] is None
    assert staging["storage_secret_key"] is None
    assert staging["storages_app_enabled"] is False


def test_staging_rechaza_el_mismo_storage_de_produccion():
    fingerprint = storage_fingerprint(
        "staging-bucket",
        "https://storage.example.test",
    )
    result = load_staging_settings(
        UNI2_STAGING_AWS_ACCESS_KEY_ID="staging-access",
        UNI2_STAGING_AWS_SECRET_ACCESS_KEY="staging-secret",
        UNI2_STAGING_AWS_STORAGE_BUCKET_NAME="staging-bucket",
        UNI2_STAGING_AWS_S3_ENDPOINT_URL="https://storage.example.test",
        UNI2_STAGING_STORAGE_FINGERPRINT=fingerprint,
        UNI2_PRODUCTION_STORAGE_FINGERPRINT=fingerprint,
    )

    assert result.returncode != 0
    assert "Staging no puede usar el storage de Producción" in result.stderr


def test_staging_usa_urls_firmadas_para_su_bucket_privado():
    fingerprint = storage_fingerprint(
        "staging-bucket",
        "https://storage.example.test",
    )
    result = load_staging_settings(
        UNI2_STAGING_AWS_ACCESS_KEY_ID="staging-access",
        UNI2_STAGING_AWS_SECRET_ACCESS_KEY="staging-secret",
        UNI2_STAGING_AWS_STORAGE_BUCKET_NAME="staging-bucket",
        UNI2_STAGING_AWS_S3_ENDPOINT_URL="https://storage.example.test",
        UNI2_STAGING_STORAGE_FINGERPRINT=fingerprint,
        UNI2_PRODUCTION_STORAGE_FINGERPRINT="d" * 64,
    )

    assert result.returncode == 0, result.stderr
    staging = json.loads(result.stdout)
    assert staging["storage_backend"] == "storages.backends.s3.S3Storage"
    assert staging["storage_access_key"] == "staging-access"
    assert staging["storage_secret_key"] == "staging-secret"
    assert staging["storage_custom_domain"] is None
    assert staging["storage_querystring_auth"] is True
    assert staging["storages_app_enabled"] is True


def test_staging_rechaza_placeholders_en_huellas_de_storage():
    result = load_staging_settings(
        UNI2_STAGING_AWS_ACCESS_KEY_ID="staging-access",
        UNI2_STAGING_AWS_SECRET_ACCESS_KEY="staging-secret",
        UNI2_STAGING_AWS_STORAGE_BUCKET_NAME="staging-bucket",
        UNI2_STAGING_STORAGE_FINGERPRINT="reemplazar",
        UNI2_PRODUCTION_STORAGE_FINGERPRINT="reemplazar",
    )

    assert result.returncode != 0
    assert "UNI2_STAGING_STORAGE_FINGERPRINT debe ser una huella SHA-256" in (
        result.stderr
    )
