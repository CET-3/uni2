from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


def content_types_huerfanos():
    return [content_type for content_type in ContentType.objects.all() if content_type.model_class() is None]


class Command(BaseCommand):
    help = "Informa o elimina permisos asociados a modelos que ya no existen."

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true", help="Elimina los residuos encontrados.")
        parser.add_argument("--check", action="store_true", help="Falla si encuentra residuos.")

    def handle(self, *args, **options):
        if options["apply"] and options["check"]:
            raise CommandError("Usá --apply o --check, no ambas opciones.")

        stale_types = content_types_huerfanos()
        if not stale_types:
            self.stdout.write(self.style.SUCCESS("No se encontraron permisos huérfanos."))
            return

        for content_type in stale_types:
            permisos = content_type.permission_set.all()
            self.stdout.write(f"{content_type.app_label}.{content_type.model}")
            for permiso in permisos:
                self.stdout.write(
                    f"  {permiso.codename}: {permiso.name} "
                    f"(grupos={permiso.group_set.count()}, usuarios={permiso.user_set.count()})"
                )

        if options["check"]:
            raise CommandError("Se encontraron permisos huérfanos.")
        if not options["apply"]:
            self.stdout.write("Ejecutá nuevamente con --apply para eliminar estos residuos.")
            return

        with transaction.atomic():
            for content_type in stale_types:
                content_type.delete()
        self.stdout.write(self.style.SUCCESS("Permisos huérfanos eliminados."))
