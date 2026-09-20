"""Copia cifrada de public en R2. Ejecutar con uv run --env-file."""

import hashlib
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import boto3


REQUIRED = (
    "DATABASE_URL",
    "R2_BUCKET",
    "R2_ENDPOINT",
    "R2_ACCESS_KEY_ID",
    "R2_SECRET_ACCESS_KEY",
    "BACKUP_PASSPHRASE",
)


def checked_environment():
    missing = [name for name in REQUIRED if not os.environ.get(name)]
    if missing:
        raise SystemExit("Faltan variables: " + ", ".join(missing))
    if len(os.environ["BACKUP_PASSPHRASE"]) < 32:
        raise SystemExit("BACKUP_PASSPHRASE debe tener al menos 32 caracteres")


def digest(path):
    result = hashlib.sha256()
    with open(path, "rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def main():
    checked_environment()
    with tempfile.TemporaryDirectory(prefix="uni2-backup-") as directory:
        root = Path(directory)
        key_file = root / "passphrase"
        key_file.write_text(os.environ["BACKUP_PASSPHRASE"], encoding="utf-8")
        key_file.chmod(0o600)
        encrypted = root / "backup.dump.gpg"
        with encrypted.open("wb") as output:
            dump = subprocess.Popen(
                ["docker", "run", "--rm", "-i", "-e", "DATABASE_URL", "-e", "PGOPTIONS", "postgres:17",
                 "sh", "-c", 'exec pg_dump --dbname="$DATABASE_URL" --schema=public '
                 '--format=custom --no-owner --no-privileges'],
                stdout=subprocess.PIPE,
                env={**os.environ, "PGOPTIONS": "-c default_transaction_read_only=on"},
            )
            encrypt = subprocess.Popen(
                ["gpg", "--batch", "--yes", "--pinentry-mode", "loopback",
                 "--passphrase-file", str(key_file), "--symmetric", "--cipher-algo", "AES256"],
                stdin=dump.stdout, stdout=output,
            )
            dump.stdout.close()
            encrypt_status = encrypt.wait()
            dump_status = dump.wait()
        if dump_status or encrypt_status or not encrypted.stat().st_size:
            raise SystemExit("Falló el dump o el cifrado; no se subió ningún objeto")

        s3 = boto3.client(
            "s3", endpoint_url=os.environ["R2_ENDPOINT"], region_name="auto",
            aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        )
        name = datetime.now(timezone.utc).strftime("uni2-%Y%m%dT%H%M%SZ.dump.gpg")
        s3.upload_file(str(encrypted), os.environ["R2_BUCKET"], name)
        downloaded = root / "downloaded.dump.gpg"
        s3.download_file(os.environ["R2_BUCKET"], name, str(downloaded))
        if digest(encrypted) != digest(downloaded):
            raise SystemExit("La copia descargada no coincide con el archivo enviado")

        decrypt = subprocess.run(
            ["gpg", "--batch", "--yes", "--pinentry-mode", "loopback",
             "--passphrase-file", str(key_file), "--decrypt", str(downloaded)],
            stdout=subprocess.DEVNULL, check=False,
        )
        if decrypt.returncode:
            raise SystemExit("La copia subida no se pudo descifrar")
        print(f"Backup verificado: {os.environ['R2_BUCKET']}/{name} ({encrypted.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
