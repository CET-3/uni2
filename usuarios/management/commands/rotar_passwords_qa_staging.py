import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from usuarios.staging import rotate_staging_qa_passwords


def _required_environment(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise CommandError(f"Falta la variable temporal {name}.")
    return value


class Command(BaseCommand):
    help = "Rota las contraseñas de las cuatro cuentas QA existentes en staging."

    def handle(self, *args, **options):
        if getattr(settings, "UNI2_DEPLOYMENT_ENVIRONMENT", "") != "staging":
            raise CommandError("Este comando sólo puede ejecutarse con settings de staging.")
        if (
            connection.vendor != "postgresql"
            and not getattr(settings, "UNI2_ALLOW_STAGING_COMMAND_ON_SQLITE", False)
        ):
            raise CommandError("La rotación operativa requiere PostgreSQL.")

        credentials = {
            "admin": {
                "username": _required_environment("UNI2_STAGING_QA_ADMIN_USERNAME"),
                "password": _required_environment("UNI2_STAGING_QA_ADMIN_PASSWORD"),
            },
            "asociado_a": {
                "username": _required_environment("UNI2_STAGING_QA_ASOCIADO_A_USERNAME"),
                "password": _required_environment("UNI2_STAGING_QA_ASOCIADO_A_PASSWORD"),
            },
            "asociado_b": {
                "username": _required_environment("UNI2_STAGING_QA_ASOCIADO_B_USERNAME"),
                "password": _required_environment("UNI2_STAGING_QA_ASOCIADO_B_PASSWORD"),
            },
            "comercio": {
                "username": _required_environment("UNI2_STAGING_QA_COMERCIO_USERNAME"),
                "password": _required_environment("UNI2_STAGING_QA_COMERCIO_PASSWORD"),
            },
        }

        try:
            result = rotate_staging_qa_passwords(credentials=credentials)
        except (ValueError, TypeError) as exc:
            raise CommandError(str(exc)) from exc
        except Exception as exc:
            raise CommandError(
                "No se completó la rotación; la transacción fue revertida."
            ) from exc

        self.stdout.write(
            self.style.SUCCESS(
                f"Contraseñas QA actualizadas: {result.usuarios_actualizados} cuentas."
            )
        )
