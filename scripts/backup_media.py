"""Copia y verifica los objetos de uni2-media en uni2-backup."""

import hashlib
import os
from datetime import datetime, timezone

import boto3


def client(access_key, secret_key):
    return boto3.client(
        "s3", endpoint_url=os.environ["R2_ENDPOINT"], region_name="auto",
        aws_access_key_id=access_key, aws_secret_access_key=secret_key,
    )


def main():
    required = (
        "R2_ENDPOINT", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY",
        "MEDIA_R2_ACCESS_KEY_ID", "MEDIA_R2_SECRET_ACCESS_KEY",
    )
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        raise SystemExit("Faltan variables: " + ", ".join(missing))

    source = client(os.environ["MEDIA_R2_ACCESS_KEY_ID"], os.environ["MEDIA_R2_SECRET_ACCESS_KEY"])
    target = client(os.environ["R2_ACCESS_KEY_ID"], os.environ["R2_SECRET_ACCESS_KEY"])
    run = os.environ.get("GITHUB_RUN_ID")
    attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "1")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    prefix = f"media/{stamp}-{run}-{attempt}/" if run else f"media/{stamp}/"
    count = size = 0
    for page in source.get_paginator("list_objects_v2").paginate(Bucket="uni2-media"):
        for item in page.get("Contents", []):
            key = item["Key"]
            body = source.get_object(Bucket="uni2-media", Key=key)["Body"]
            try:
                data = body.read()
            finally:
                body.close()
            if len(data) != item["Size"]:
                raise SystemExit(f"Tamaño distinto al leer {key}")
            backup_key = prefix + key
            target.put_object(Bucket="uni2-backup", Key=backup_key, Body=data)
            copied = target.get_object(Bucket="uni2-backup", Key=backup_key)["Body"]
            try:
                verified = hashlib.sha256(copied.read()).digest() == hashlib.sha256(data).digest()
            finally:
                copied.close()
            if not verified:
                raise SystemExit(f"SHA-256 distinto en {backup_key}")
            count += 1
            size += len(data)
    if not count:
        raise SystemExit("uni2-media no tiene objetos; revisar antes de aceptar este backup")
    print(f"Imágenes verificadas: {count} objetos, {size} bytes en uni2-backup/{prefix}")


if __name__ == "__main__":
    main()
