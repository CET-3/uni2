import os
import re
import secrets

from django.core.exceptions import ImproperlyConfigured

from config.database_identity import (
    database_fingerprint,
    database_role_fingerprint,
    storage_fingerprint,
)

# Staging nunca puede activar correo real, aunque una variable del proyecto se
# haya copiado por error desde Producción. Se fuerza la barrera antes de
# importar ese perfil para que tampoco intente validar credenciales SMTP.
os.environ["UNI2_TRANSACTIONAL_EMAIL_MODE"] = "disabled"

from .production import *  # noqa: F403


def _required_environment(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise ImproperlyConfigured(f"Staging requiere la variable {name}.")
    return value


def _required_fingerprint(name):
    value = _required_environment(name)
    if not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ImproperlyConfigured(
            f"{name} debe ser una huella SHA-256 hexadecimal de 64 caracteres."
        )
    return value


if os.environ.get("UNI2_ENVIRONMENT") != "staging":
    raise ImproperlyConfigured("El perfil staging requiere UNI2_ENVIRONMENT=staging.")

UNI2_DEPLOYMENT_ENVIRONMENT = "staging"
GOOGLE_ANALYTICS_MEASUREMENT_ID = ""
UNI2_ENVIRONMENT_LABEL = "STAGING · DATOS REALES"
UNI2_ENVIRONMENT_SHORT_LABEL = "STAGING"
UNI2_STAGING_ACCESS_USERNAME = _required_environment("UNI2_STAGING_ACCESS_USERNAME")
UNI2_STAGING_ACCESS_PASSWORD = _required_environment("UNI2_STAGING_ACCESS_PASSWORD")
UNI2_STAGING_DATABASE_LABEL = _required_environment("UNI2_STAGING_DATABASE_LABEL")

PWA_PRIVATE_DATA_EPOCH = _required_environment("UNI2_PRIVATE_DATA_EPOCH")
PWA_APP_NAME = "UNI2 - Entorno de prueba"
PWA_SHORT_NAME = "UNI2 STG"
PWA_DESCRIPTION = "Entorno protegido de prueba de la Mutual Escolar del CET 3."
PWA_THEME_COLOR = "#a83a00"
PWA_THEME_COLOR_LIGHT = "#fff4e8"
PWA_THEME_COLOR_DARK = "#2a1208"
PWA_BACKGROUND_COLOR = "#fff4e8"
PWA_ICON_DIRECTORY = "pwa/icons/staging"

EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"
UNI2_TRANSACTIONAL_EMAIL_MODE = "disabled"
UNI2_BATCH_EMAIL_MODE = "disabled"
UNI2_WEB_PUSH_MODE = "disabled"
ALLOW_DEMO_DATA = False

MIDDLEWARE.insert(1, "config.middleware.StagingAccessMiddleware")  # noqa: F405

if DATABASES["default"]["ENGINE"] != "django.db.backends.postgresql":  # noqa: F405
    raise ImproperlyConfigured("Staging requiere una base PostgreSQL separada.")
if len(SECRET_KEY) < 32:  # noqa: F405
    raise ImproperlyConfigured("SECRET_KEY de staging debe tener al menos 32 caracteres.")
if len(UNI2_STAGING_ACCESS_PASSWORD) < 20:
    raise ImproperlyConfigured(
        "UNI2_STAGING_ACCESS_PASSWORD debe tener al menos 20 caracteres."
    )
if secrets.compare_digest(UNI2_STAGING_ACCESS_PASSWORD, SECRET_KEY):  # noqa: F405
    raise ImproperlyConfigured("La barrera HTTP no puede reutilizar SECRET_KEY.")
if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]{5,63}", PWA_PRIVATE_DATA_EPOCH):
    raise ImproperlyConfigured("UNI2_PRIVATE_DATA_EPOCH tiene un formato inválido.")

_actual_database_fingerprint = database_fingerprint(DATABASES["default"])  # noqa: F405
_actual_database_role_fingerprint = database_role_fingerprint(  # noqa: F405
    DATABASES["default"]  # noqa: F405
)
_declared_staging_fingerprint = _required_fingerprint(
    "UNI2_STAGING_DATABASE_FINGERPRINT"
)
_production_fingerprint = _required_fingerprint(
    "UNI2_PRODUCTION_DATABASE_FINGERPRINT"
)
_declared_staging_role_fingerprint = _required_fingerprint(
    "UNI2_STAGING_DATABASE_ROLE_FINGERPRINT"
)
_production_role_fingerprint = _required_fingerprint(
    "UNI2_PRODUCTION_DATABASE_ROLE_FINGERPRINT"
)

if not secrets.compare_digest(_actual_database_fingerprint, _declared_staging_fingerprint):
    raise ImproperlyConfigured(
        "DATABASE_URL no coincide con UNI2_STAGING_DATABASE_FINGERPRINT."
    )
if secrets.compare_digest(_actual_database_fingerprint, _production_fingerprint):
    raise ImproperlyConfigured("Staging no puede usar la base de Producción.")
if not secrets.compare_digest(
    _actual_database_role_fingerprint,
    _declared_staging_role_fingerprint,
):
    raise ImproperlyConfigured(
        "El rol de DATABASE_URL no coincide con UNI2_STAGING_DATABASE_ROLE_FINGERPRINT."
    )
if secrets.compare_digest(
    _actual_database_role_fingerprint,
    _production_role_fingerprint,
):
    raise ImproperlyConfigured("Staging no puede reutilizar el rol PostgreSQL productivo.")

# Nunca se heredan credenciales o destinos media con los nombres productivos.
# Sin configuración staging explícita, las fotos quedan temporalmente no
# disponibles en el filesystem efímero de la función.
STORAGES["default"] = {"BACKEND": "django.core.files.storage.FileSystemStorage"}  # noqa: F405
if "storages" in INSTALLED_APPS:  # noqa: F405
    INSTALLED_APPS.remove("storages")  # noqa: F405
AWS_ACCESS_KEY_ID = None
AWS_SECRET_ACCESS_KEY = None
AWS_STORAGE_BUCKET_NAME = ""
AWS_S3_ENDPOINT_URL = None
AWS_S3_CUSTOM_DOMAIN = None
AWS_S3_REGION_NAME = None
AWS_QUERYSTRING_AUTH = True
AWS_QUERYSTRING_EXPIRE = 900
AWS_DEFAULT_ACL = None
AWS_S3_OBJECT_PARAMETERS = {}

_staging_bucket = os.environ.get("UNI2_STAGING_AWS_STORAGE_BUCKET_NAME", "").strip()
if _staging_bucket:
    _staging_access_key = _required_environment("UNI2_STAGING_AWS_ACCESS_KEY_ID")
    _staging_secret_key = _required_environment("UNI2_STAGING_AWS_SECRET_ACCESS_KEY")
    _staging_endpoint = os.environ.get("UNI2_STAGING_AWS_S3_ENDPOINT_URL", "").strip()
    _actual_storage_fingerprint = storage_fingerprint(
        _staging_bucket,
        _staging_endpoint,
    )
    _declared_storage_fingerprint = _required_fingerprint(
        "UNI2_STAGING_STORAGE_FINGERPRINT"
    )
    _production_storage_fingerprint = _required_fingerprint(
        "UNI2_PRODUCTION_STORAGE_FINGERPRINT"
    )
    if not secrets.compare_digest(
        _actual_storage_fingerprint,
        _declared_storage_fingerprint,
    ):
        raise ImproperlyConfigured(
            "El storage configurado no coincide con UNI2_STAGING_STORAGE_FINGERPRINT."
        )
    if secrets.compare_digest(
        _actual_storage_fingerprint,
        _production_storage_fingerprint,
    ):
        raise ImproperlyConfigured("Staging no puede usar el storage de Producción.")

    if "storages" not in INSTALLED_APPS:  # noqa: F405
        INSTALLED_APPS.append("storages")  # noqa: F405
    AWS_STORAGE_BUCKET_NAME = _staging_bucket
    AWS_ACCESS_KEY_ID = _staging_access_key
    AWS_SECRET_ACCESS_KEY = _staging_secret_key
    AWS_S3_ENDPOINT_URL = _staging_endpoint or None
    AWS_S3_REGION_NAME = os.environ.get("UNI2_STAGING_AWS_S3_REGION_NAME", "auto")
    # El bucket staging no tiene dominio público: Django entrega URLs firmadas
    # y breves. Así, el almacenamiento remoto tampoco queda mezclado con el
    # origen público productivo.
    AWS_S3_CUSTOM_DOMAIN = None
    AWS_QUERYSTRING_AUTH = True
    AWS_QUERYSTRING_EXPIRE = 900
    AWS_DEFAULT_ACL = None
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "private, no-store"}
    STORAGES["default"] = {"BACKEND": "storages.backends.s3.S3Storage"}  # noqa: F405
