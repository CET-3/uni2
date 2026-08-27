import json
import os
import subprocess
import sys

from django.conf import settings


def test_tests_capturan_correo_en_memoria():
    assert settings.EMAIL_BACKEND == "django.core.mail.backends.locmem.EmailBackend"
    assert settings.UNI2_SITE_URL == "http://testserver"


def test_desarrollo_local_muestra_correos_en_consola():
    environment = os.environ.copy()
    environment.pop("EMAIL_BACKEND", None)
    environment.pop("UNI2_SITE_URL", None)
    environment["UNI2_TRANSACTIONAL_EMAIL_MODE"] = "enabled"
    script = """
import json
from config.settings import local

print(json.dumps({
    "backend": local.EMAIL_BACKEND,
    "transactional_email_mode": local.UNI2_TRANSACTIONAL_EMAIL_MODE,
    "site_url": local.UNI2_SITE_URL,
}))
"""

    result = subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        capture_output=True,
        env=environment,
        text=True,
    )

    assert json.loads(result.stdout) == {
        "backend": "django.core.mail.backends.console.EmailBackend",
        "transactional_email_mode": "enabled",
        "site_url": "http://localhost:8000",
    }
