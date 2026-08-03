import hashlib


def database_fingerprint(database_config):
    """Identifica una base sin incluir ni exponer su contraseña."""

    host = str(database_config.get("HOST") or "").strip().lower()
    port = str(database_config.get("PORT") or "5432").strip()
    name = str(database_config.get("NAME") or "").strip()
    identity = f"{host}:{port}/{name}"
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def database_role_fingerprint(database_config):
    """Identifica el rol de conexión sin exponer su nombre."""

    host = str(database_config.get("HOST") or "").strip().lower()
    user = str(database_config.get("USER") or "").strip()
    identity = f"{user}@{host}"
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def storage_fingerprint(bucket, endpoint="", custom_domain=""):
    """Identifica un destino de media sin incluir claves de acceso."""

    identity = "|".join(
        (
            str(bucket).strip().lower(),
            str(endpoint).strip().lower().rstrip("/"),
            str(custom_domain).strip().lower().rstrip("/"),
        )
    )
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()
