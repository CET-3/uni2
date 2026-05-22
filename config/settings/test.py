from .base import *  # noqa: F403


if DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3":  # noqa: F405
    DATABASES["default"]["NAME"] = str(BASE_DIR / "test.sqlite3")  # noqa: F405
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
