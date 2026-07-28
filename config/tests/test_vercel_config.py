import json
from pathlib import Path

from django.core.management import call_command
from django.test import override_settings


BASE_DIR = Path(__file__).resolve().parents[2]


def test_vercel_recolecta_estaticos_y_despliega_solo_main():
    config = json.loads((BASE_DIR / "vercel.json").read_text(encoding="utf-8"))

    assert config["buildCommand"] == "python manage.py collectstatic --noinput"
    assert config["git"]["deploymentEnabled"] == {
        "*": False,
        "main": True,
    }


def test_collectstatic_genera_el_manifest_de_whitenoise(tmp_path):
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
    assert manifest["paths"]["js/uni2-theme.js"].startswith("js/uni2-theme.")
