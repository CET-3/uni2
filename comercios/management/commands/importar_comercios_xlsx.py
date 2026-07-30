from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from comercios.importers import analyze_comercios_xlsx, import_comercios_preview


class Command(BaseCommand):
    help = "Analiza o importa la planilla inicial de comercios en formato .xlsx."

    def add_arguments(self, parser):
        parser.add_argument("xlsx_path", help="Ruta de la planilla .xlsx.")
        parser.add_argument(
            "--confirmar",
            action="store_true",
            help="Guarda los comercios analizados. Sin esta opción no modifica la base.",
        )

    def handle(self, *args, **options):
        path = Path(options["xlsx_path"])
        if path.suffix.lower() != ".xlsx":
            raise CommandError("La planilla de comercios debe tener extensión .xlsx.")

        try:
            with path.open("rb") as xlsx_file:
                preview = analyze_comercios_xlsx(xlsx_file)
        except (OSError, RuntimeError, ValueError) as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(f'Hoja analizada: "{preview.hoja}"')
        self.stdout.write(f"Comercios encontrados: {len(preview.filas)}")
        self.stdout.write(f"Actividades comerciales: {preview.cantidad_actividades}")
        self.stdout.write(f"Fotos embebidas: {preview.cantidad_fotos}")

        for warning in preview.advertencias:
            self.stdout.write(self.style.WARNING(f"Advertencia: {warning}"))
        for error in preview.errores:
            self.stdout.write(self.style.ERROR(f"Error: {error}"))

        if not preview.es_valida:
            raise CommandError(
                f"La planilla tiene {len(preview.errores)} error(es). "
                "No se modificó la base de datos."
            )

        if not options["confirmar"]:
            self.stdout.write(
                self.style.WARNING(
                    "Análisis finalizado sin guardar datos. "
                    "Repetí el comando con --confirmar para importar."
                )
            )
            return

        try:
            result = import_comercios_preview(preview)
        except (ValidationError, ValueError) as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(
            self.style.SUCCESS(
                "Importación finalizada. "
                f"Comercios creados: {result.comercios_creados}. "
                f"Comercios actualizados: {result.comercios_actualizados}. "
                f"Actividades creadas: {result.actividades_creadas}. "
                f"Fotos asignadas: {result.fotos_asignadas}."
            )
        )
