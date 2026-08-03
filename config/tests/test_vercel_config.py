import json
import os
from pathlib import Path

from django.core.management import call_command
from django.test import override_settings

from manage import configure_settings_module


BASE_DIR = Path(__file__).resolve().parents[2]


def test_vercel_usa_django_zero_config_y_reserva_git_para_produccion():
    config = json.loads((BASE_DIR / "vercel.json").read_text(encoding="utf-8"))

    assert config["framework"] == "django"
    assert config["git"]["deploymentEnabled"] == {
        "**": False,
        "main": True,
    }
    assert config["regions"] == ["gru1"]
    assert "buildCommand" not in config
    assert "functions" not in config
    assert "routes" not in config


def test_manage_usa_settings_locales_fuera_de_vercel(monkeypatch):
    monkeypatch.delenv("DJANGO_SETTINGS_MODULE", raising=False)
    monkeypatch.delenv("VERCEL", raising=False)

    configure_settings_module()

    assert os.environ["DJANGO_SETTINGS_MODULE"] == "config.settings.local"


def test_manage_usa_settings_productivos_en_vercel(monkeypatch):
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "")
    monkeypatch.setenv("VERCEL", "1")

    configure_settings_module()

    assert os.environ["DJANGO_SETTINGS_MODULE"] == "config.settings.production"


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
