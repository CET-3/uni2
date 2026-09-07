import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


REQUIRED_ENVIRONMENT = (
    "DJANGO_SETTINGS_MODULE",
    "UNI2_ENVIRONMENT",
    "SECRET_KEY",
    "DATABASE_URL",
    "UNI2_STAGING_ACCESS_USERNAME",
    "UNI2_STAGING_ACCESS_PASSWORD",
    "UNI2_STAGING_DATABASE_LABEL",
    "UNI2_STAGING_DATABASE_FINGERPRINT",
    "UNI2_PRODUCTION_DATABASE_FINGERPRINT",
    "UNI2_STAGING_DATABASE_ROLE_FINGERPRINT",
    "UNI2_PRODUCTION_DATABASE_ROLE_FINGERPRINT",
    "UNI2_PRIVATE_DATA_EPOCH",
)


def pending_migrations():
    """Devuelve las migraciones que *migrate* aplicaría, sin escribir nada."""

    executor = MigrationExecutor(connection)
    targets = executor.loader.graph.leaf_nodes()
    return [
        f"{migration.app_label}.{migration.name}"
        for migration, backwards in executor.migration_plan(targets)
        if not backwards
    ]


class Command(BaseCommand):
    help = "Verifica el entorno y el plan antes de desplegar o migrar staging."

    def add_arguments(self, parser):
        parser.add_argument(
            "--expected-migration",
            action="append",
            dest="expected_migrations",
            help=(
                "Migración esperada (app.nombre). Se puede repetir; si se usa, "
                "el plan debe coincidir exactamente."
            ),
        )

    def handle(self, *args, **options):
        errors = []
        missing = [name for name in REQUIRED_ENVIRONMENT if not os.getenv(name, "").strip()]
        if missing:
            errors.append("faltan variables: " + ", ".join(missing))

        if os.getenv("DJANGO_SETTINGS_MODULE") != "config.settings.staging":
            errors.append("DJANGO_SETTINGS_MODULE debe ser config.settings.staging")
        if os.getenv("UNI2_ENVIRONMENT") != "staging":
            errors.append("UNI2_ENVIRONMENT=staging es obligatorio")
        if getattr(settings, "UNI2_DEPLOYMENT_ENVIRONMENT", "") != "staging":
            errors.append("el perfil Django cargado no es staging")
        if settings.DATABASES["default"]["ENGINE"] != "django.db.backends.postgresql":
            errors.append("staging requiere una base PostgreSQL")

        try:
            migrations = pending_migrations()
        except Exception as error:  # pragma: no cover - el detalle depende del driver
            errors.append(f"no se pudo leer el plan de migraciones: {error}")
            migrations = []

        expected = options.get("expected_migrations")
        if expected is not None and migrations != expected:
            errors.append(
                "el plan de migraciones no coincide: "
                f"esperadas={expected or 'ninguna'}, actuales={migrations or 'ninguna'}"
            )

        if errors:
            raise CommandError("Preflight staging rechazado:\n- " + "\n- ".join(errors))

        self.stdout.write(self.style.SUCCESS("Preflight staging aprobado"))
        self.stdout.write(f"Migraciones pendientes: {len(migrations)}")
        for migration in migrations:
            self.stdout.write(f"- {migration}")
