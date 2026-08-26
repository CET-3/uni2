import json
import os
import subprocess
import sys

from django.conf import settings
from django.core.management import call_command
from django.test import override_settings


def test_pwa_esta_instalada_y_middleware_corre_despues_de_autenticacion():
    assert "pwa" in settings.INSTALLED_APPS
    auth_index = settings.MIDDLEWARE.index("django.contrib.auth.middleware.AuthenticationMiddleware")
    pwa_index = settings.MIDDLEWARE.index("pwa.middleware.PWACacheControlMiddleware")
    assert pwa_index > auth_index
    assert settings.PWA_CREDENTIAL_OFFLINE_TTL_DAYS == 7


def test_build_id_productivo_proviene_del_commit_de_vercel():
    environment = os.environ.copy()
    environment.update(
        {
            "DATABASE_URL": "sqlite:///:memory:",
            "SECRET_KEY": "test-secret-key",
            "UNI2_TRANSACTIONAL_EMAIL_MODE": "disabled",
            "VERCEL_GIT_COMMIT_SHA": "abc123def456",
        }
    )
    script = """
import json
from config.settings import production
print(json.dumps({
    "build_id": production.PWA_BUILD_ID,
    "ttl_days": production.PWA_CREDENTIAL_OFFLINE_TTL_DAYS,
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
        "build_id": "abc123def456",
        "ttl_days": 7,
    }


def test_collectstatic_incluye_assets_pwa_vendor_e_iconos(tmp_path):
    storages = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }

    with override_settings(STATIC_ROOT=tmp_path, STORAGES=storages):
        call_command("collectstatic", interactive=False, verbosity=0)

    manifest = json.loads((tmp_path / "staticfiles.json").read_text(encoding="utf-8"))
    expected_paths = {
        "pwa/uni2-pwa.js",
        "pwa/uni2-private-storage.js",
        "pwa/uni2-credential.js",
        "pwa/icons/icon-192.png",
        "pwa/icons/icon-512.png",
        "pwa/icons/icon-maskable-192.png",
        "pwa/icons/icon-maskable-512.png",
        "pwa/icons/apple-touch-icon-180.png",
        "pwa/icons/staging/icon-192.png",
        "pwa/icons/staging/icon-512.png",
        "pwa/icons/staging/icon-maskable-192.png",
        "pwa/icons/staging/icon-maskable-512.png",
        "pwa/icons/staging/apple-touch-icon-180.png",
        "pwa/icons/staging/favicon-32.png",
        "vendor/bootstrap/5.3.3/css/bootstrap.min.css",
        "vendor/bootstrap/5.3.3/js/bootstrap.bundle.min.js",
        "vendor/bootstrap-icons/1.11.3/font/bootstrap-icons.min.css",
        "vendor/bootstrap-icons/1.11.3/font/fonts/bootstrap-icons.woff2",
        "vendor/qrcode-generator/1.4.4/qrcode.min.js",
    }
    assert expected_paths <= manifest["paths"].keys()


def test_almacenamiento_privado_invalida_credenciales_al_cambiar_epoch():
    source = (settings.BASE_DIR / "static/pwa/uni2-private-storage.js").read_text()

    assert "dataEpoch: DATA_EPOCH" in source
    assert "record.dataEpoch !== DATA_EPOCH" in source
    assert "await deleteActiveCredential()" in source
