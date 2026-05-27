import os

import dj_database_url

from .base import *  # noqa: F403

DEBUG = False

SECRET_KEY = os.environ["SECRET_KEY"]

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")

# --- Base de datos ----------------------------------------------------------
DATABASES = {
    "default": dj_database_url.config(
        env="DATABASE_URL",
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# --- Archivos estáticos (WhiteNoise) ----------------------------------------
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405

STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
