from django.core.management.base import BaseCommand, CommandError

from usuarios.group_configuration import (
    inspect_group_configuration,
    sync_group_configuration,
)


class Command(BaseCommand):
    help = "Verifica o aplica la matriz de grupos y permisos administrada por Uni2."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Aplica los cambios. Sin esta opción, el comando sólo informa.",
        )
        parser.add_argument(
            "--check",
            action="store_true",
            help="Finaliza con error si encuentra diferencias; útil para CI.",
        )

    def handle(self, *args, **options):
        if options["apply"] and options["check"]:
            raise CommandError("Usá --apply o --check, no ambas opciones.")

        result = (
            sync_group_configuration()
            if options["apply"]
            else inspect_group_configuration()
        )
        if not result.has_drift:
            self.stdout.write(
                self.style.SUCCESS("La matriz de grupos está sincronizada.")
            )
            return

        if result.created_groups:
            self.stdout.write("Grupos faltantes: " + ", ".join(result.created_groups))
        if result.changed_groups:
            self.stdout.write(
                "Grupos con permisos diferentes: " + ", ".join(result.changed_groups)
            )
        if result.missing_permissions:
            self.stdout.write(
                "Permisos inexistentes: "
                + ", ".join(sorted(set(result.missing_permissions)))
            )
        if options["apply"]:
            self.stdout.write(
                self.style.SUCCESS("La matriz de grupos fue sincronizada.")
            )
        elif options["check"]:
            raise CommandError("La matriz de grupos no está sincronizada.")
        else:
            self.stdout.write(
                "Ejecutá nuevamente con --apply para aplicar estos cambios."
            )
