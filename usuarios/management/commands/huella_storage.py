from django.core.management.base import BaseCommand

from config.database_identity import storage_fingerprint


class Command(BaseCommand):
    help = "Calcula la huella de un bucket media sin usar ni mostrar sus claves."

    def add_arguments(self, parser):
        parser.add_argument("--bucket", required=True)
        parser.add_argument("--endpoint", default="")
        parser.add_argument("--custom-domain", default="")

    def handle(self, *args, **options):
        self.stdout.write(
            storage_fingerprint(
                options["bucket"],
                options["endpoint"],
                options["custom_domain"],
            )
        )
