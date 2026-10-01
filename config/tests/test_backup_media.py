from io import BytesIO

import pytest

from scripts import backup_media


class Source:
    def get_paginator(self, operation):
        assert operation == "list_objects_v2"
        return self

    def paginate(self, **kwargs):
        assert kwargs == {"Bucket": "uni2-media"}
        return [{"Contents": [{"Key": "comercios/foto.jpg", "Size": 4}]}]

    def get_object(self, **kwargs):
        return {"Body": BytesIO(b"foto")}


class Target:
    def __init__(self, corrupted=False):
        self.corrupted = corrupted
        self.objects = {}

    def put_object(self, Bucket, Key, Body):
        assert Bucket == "uni2-backup"
        self.objects[Key] = Body

    def get_object(self, Bucket, Key):
        return {"Body": BytesIO(b"otro" if self.corrupted else self.objects[Key])}


@pytest.mark.parametrize("corrupted", [False, True])
def test_media_backup_checks_downloaded_hash(monkeypatch, corrupted, capsys):
    for name in (
        "R2_ENDPOINT", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY",
        "MEDIA_R2_ACCESS_KEY_ID", "MEDIA_R2_SECRET_ACCESS_KEY",
    ):
        monkeypatch.setenv(name, "test")
    monkeypatch.delenv("GITHUB_RUN_ID", raising=False)
    target = Target(corrupted)
    monkeypatch.setattr(backup_media, "client", lambda key, secret: Source() if key == "media" else target)
    monkeypatch.setenv("MEDIA_R2_ACCESS_KEY_ID", "media")

    if corrupted:
        with pytest.raises(SystemExit, match="SHA-256 distinto"):
            backup_media.main()
    else:
        backup_media.main()
        assert next(iter(target.objects)).endswith("/comercios/foto.jpg")
        assert "1 objetos, 4 bytes" in capsys.readouterr().out
