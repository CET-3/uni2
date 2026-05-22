from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from asociados.models import Colegio, Curso
from contabilidad.models import CuentaContable
from usuarios.services import ADMIN_GROUP, ensure_default_groups


class Command(BaseCommand):
    help = "Carga datos iniciales para desarrollo local de Uni2."

    def handle(self, *args, **options):
        ensure_default_groups()

        colegio, _ = Colegio.objects.get_or_create(
            nombre="CET 3",
            defaults={"direccion": "", "telefono": "", "email": "", "activo": True},
        )

        cursos = ["1° 1°", "1° 2°", "2° 1°", "2° 2°", "3° 1°", "3° 2°"]
        for nombre in cursos:
            Curso.objects.get_or_create(colegio=colegio, nombre=nombre, defaults={"activo": True})

        cuentas = [
            ("1.1.01", "Caja", CuentaContable.TIPO_ACTIVO),
            ("1.1.02", "Billetera virtual", CuentaContable.TIPO_ACTIVO),
            ("4.1.01", "Ingresos por cuotas", CuentaContable.TIPO_INGRESO),
        ]
        for codigo, nombre, tipo in cuentas:
            CuentaContable.objects.get_or_create(
                codigo=codigo,
                defaults={"nombre": nombre, "tipo": tipo, "activa": True},
            )

        user_model = get_user_model()
        if not user_model.objects.filter(username="admin").exists():
            admin = user_model.objects.create_superuser(
                username="admin",
                email="admin@example.com",
                password="admin1234",
            )
            admin.groups.add(admin.groups.model.objects.get(name=ADMIN_GROUP))

        self.stdout.write(self.style.SUCCESS(f"Datos iniciales cargados al {date.today()}"))
