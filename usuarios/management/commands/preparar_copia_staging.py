import os
import re

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from usuarios.staging import harden_staging_clone


REFRESH_ID_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{5,63}$")


def _required_environment(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise CommandError(f"Falta la variable temporal {name}.")
    return value


class Command(BaseCommand):
    help = "Invalida credenciales productivas en una copia aislada para staging."

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

        qa_admin_username = _required_environment("UNI2_STAGING_QA_ADMIN_USERNAME")
        qa_admin_password = _required_environment("UNI2_STAGING_QA_ADMIN_PASSWORD")
        qa_asociado_a_username = _required_environment(
            "UNI2_STAGING_QA_ASOCIADO_A_USERNAME"
        )
        qa_asociado_a_password = _required_environment(
            "UNI2_STAGING_QA_ASOCIADO_A_PASSWORD"
        )
        qa_asociado_b_username = _required_environment(
            "UNI2_STAGING_QA_ASOCIADO_B_USERNAME"
        )
        qa_asociado_b_password = _required_environment(
            "UNI2_STAGING_QA_ASOCIADO_B_PASSWORD"
        )
        qa_comercio_username = _required_environment(
            "UNI2_STAGING_QA_COMERCIO_USERNAME"
        )
        qa_comercio_password = _required_environment(
            "UNI2_STAGING_QA_COMERCIO_PASSWORD"
        )

        try:
            result = harden_staging_clone(
                qa_admin_username=qa_admin_username,
                qa_admin_password=qa_admin_password,
                refresh_id=refresh_id,
                qa_asociado_a_username=qa_asociado_a_username,
                qa_asociado_a_password=qa_asociado_a_password,
                qa_asociado_b_username=qa_asociado_b_username,
                qa_asociado_b_password=qa_asociado_b_password,
                qa_comercio_username=qa_comercio_username,
                qa_comercio_password=qa_comercio_password,
            )
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
                f"{result.usuarios_invalidados} usuarios invalidados, "
                f"{result.tokens_regenerados} tokens regenerados y "
                f"{result.usuarios_qa_creados} usuarios QA creados."
            )
        )
