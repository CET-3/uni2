from django.core.management.base import BaseCommand, CommandError

from asociados.services import import_asociados_from_csv


class Command(BaseCommand):
    help = "Importa asociados desde un archivo CSV."

    def add_arguments(self, parser):
        parser.add_argument("csv_path")

    def handle(self, *args, **options):
        try:
            with open(options["csv_path"], "r", encoding="utf-8", newline="") as csv_file:
                result = import_asociados_from_csv(csv_file)
        except FileNotFoundError as exc:
            raise CommandError(str(exc)) from exc

        if result.errors:
            for error in result.errors:
                self.stdout.write(self.style.WARNING(error))
        self.stdout.write(self.style.SUCCESS(f"Asociados creados: {result.created}"))

