import os

import dj_database_url

from .base import *  # noqa: F403

DEBUG = os.environ.get("DEBUG", "False") == "True"

SECRET_KEY = os.environ["SECRET_KEY"]

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")

# --- Base de datos ----------------------------------------------------------
DATABASES = {
    "default": dj_database_url.config(
        env="DATABASE_URL",
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# --- Archivos estáticos (CDN de Vercel) -------------------------------------
# Vercel sirve el directorio public/ como CDN; los estáticos van en public/static/
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "public" / "static"  # noqa: F405
