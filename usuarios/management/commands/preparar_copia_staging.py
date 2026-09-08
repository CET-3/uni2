import re

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from usuarios.staging import harden_staging_clone


REFRESH_ID_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{5,63}$")


class Command(BaseCommand):
    help = "Conserva usuarios y elimina sesiones copiadas para habilitar staging."

    def add_arguments(self, parser):
        parser.add_argument("--refresh-id", required=True)
        parser.add_argument("--confirm-target", required=True)

    def handle(self, *args, **options):
        if getattr(settings, "UNI2_DEPLOYMENT_ENVIRONMENT", "") != "staging":
            raise CommandError("Este comando sólo puede ejecutarse con settings de staging.")
        if (
            connection.vendor != "postgresql"
            and not getattr(settings, "UNI2_ALLOW_STAGING_COMMAND_ON_SQLITE", False)
        ):
            raise CommandError("El endurecimiento operativo requiere PostgreSQL.")

        refresh_id = options["refresh_id"]
        if not REFRESH_ID_PATTERN.fullmatch(refresh_id):
            raise CommandError("El refresh ID tiene un formato inválido.")
        if options["confirm_target"] != settings.UNI2_STAGING_DATABASE_LABEL:
            raise CommandError("La confirmación no coincide con la base staging configurada.")
        if refresh_id != settings.PWA_PRIVATE_DATA_EPOCH:
            raise CommandError(
                "UNI2_PRIVATE_DATA_EPOCH debe coincidir con --refresh-id antes del endurecimiento."
            )

        try:
            result = harden_staging_clone(refresh_id=refresh_id)
        except (ValueError, TypeError) as exc:
            raise CommandError(str(exc)) from exc
        except Exception as exc:
            raise CommandError(
                "No se completó el endurecimiento; la transacción fue revertida."
            ) from exc

        self.stdout.write(
            self.style.SUCCESS(
                "Copia endurecida: "
                f"{result.sesiones_eliminadas} sesiones eliminadas, "
                f"{result.usuarios_conservados} usuarios conservados."
            )
        )
