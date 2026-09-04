import os

from .base import *  # noqa: F403


DEBUG = True
ALLOW_DEMO_DATA = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "192.168.18.138"]
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
UNI2_TRANSACTIONAL_EMAIL_MODE = os.getenv(
    "UNI2_TRANSACTIONAL_EMAIL_MODE", "enabled"
)
