import os
from pathlib import Path

import pytest

from scripts import backup_production


def test_backup_rechaza_una_descarga_corrupta(tmp_path, monkeypatch):
    docker = tmp_path / "docker"
    docker.write_text("#!/bin/sh\nprintf 'PGDMPbackup-de-prueba'\n")
    docker.chmod(0o755)
    monkeypatch.setenv("PATH", f"{tmp_path}:{os.environ['PATH']}")
    for name, value in {
        "DATABASE_URL": "postgresql://example.test/fake",
        "R2_BUCKET": "bucket-de-prueba",
        "R2_ENDPOINT": "https://example.test",
        "R2_ACCESS_KEY_ID": "test-key",
        "R2_SECRET_ACCESS_KEY": "test-secret",
        "BACKUP_PASSPHRASE": "frase-de-prueba-larga-y-unica-123456789",
    }.items():
        monkeypatch.setenv(name, value)

    class R2Corrupto:
        def upload_file(self, filename, bucket, name):
            self.bytes = Path(filename).read_bytes()

        def download_file(self, bucket, name, filename):
            Path(filename).write_bytes(self.bytes + b"corrupto")

    monkeypatch.setattr(backup_production.boto3, "client", lambda *args, **kwargs: R2Corrupto())

    with pytest.raises(SystemExit, match="no coincide"):
        backup_production.main()
