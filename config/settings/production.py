import os

import dj_database_url

from .base import *  # noqa: F403


def _env_list(name):
    return [value.strip() for value in os.environ.get(name, "").split(",") if value.strip()]


def _unique(values):
    return list(dict.fromkeys(values))


DEBUG = False

SECRET_KEY = os.environ["SECRET_KEY"]

_vercel_hosts = [
    host
    for variable in ("VERCEL_URL", "VERCEL_BRANCH_URL", "VERCEL_PROJECT_PRODUCTION_URL")
    if (host := os.environ.get(variable))
]

ALLOWED_HOSTS = _unique([*_env_list("ALLOWED_HOSTS"), *_vercel_hosts])
CSRF_TRUSTED_ORIGINS = _unique(
    [*_env_list("CSRF_TRUSTED_ORIGINS"), *(f"https://{host}" for host in _vercel_hosts)]
)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 3600

# --- Base de datos ----------------------------------------------------------
DATABASES = {
    "default": dj_database_url.config(
        env="DATABASE_URL",
        conn_max_age=0,
        conn_health_checks=False,
    )
}

# --- Archivos estáticos (WhiteNoise) ----------------------------------------
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405
STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# --- Archivos subidos por usuarios ------------------------------------------
# Vercel no ofrece filesystem persistente para uploads. Si se define un bucket
# S3-compatible, las fotos se guardan fuera del runtime serverless.
if os.environ.get("AWS_STORAGE_BUCKET_NAME"):
    INSTALLED_APPS.append("storages")  # noqa: F405
    AWS_STORAGE_BUCKET_NAME = os.environ["AWS_STORAGE_BUCKET_NAME"]
    AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME", "auto")
    AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
    AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
    AWS_S3_ENDPOINT_URL = os.environ.get("AWS_S3_ENDPOINT_URL")
    AWS_S3_CUSTOM_DOMAIN = os.environ.get("AWS_S3_CUSTOM_DOMAIN")
    AWS_QUERYSTRING_AUTH = False
    AWS_DEFAULT_ACL = "public-read"
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
    STORAGES["default"] = {"BACKEND": "storages.backends.s3.S3Storage"}
