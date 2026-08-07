from django.conf import settings
from django.core.management.base import BaseCommand

from config.database_identity import database_fingerprint, database_role_fingerprint


class Command(BaseCommand):
    help = "Muestra una huella no reversible del host y nombre de la base configurada."

    def add_arguments(self, parser):
        parser.add_argument(
            "--rol",
            action="store_true",
            help="Muestra la huella separada del rol y host de conexión.",
        )

    def handle(self, *args, **options):
        database = settings.DATABASES["default"]
        fingerprint = (
            database_role_fingerprint(database)
            if options["rol"]
            else database_fingerprint(database)
        )
        self.stdout.write(fingerprint)
