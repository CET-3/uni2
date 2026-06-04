from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from asociados.models import Curso
from comercios.models import ActividadComercial, Comercio
from contenidos.models import Beneficio
from contabilidad.models import CuentaContable
from usuarios.services import ADMIN_GROUP, ensure_default_groups


class Command(BaseCommand):
    help = "Carga datos iniciales para desarrollo local de Uni2."

    def handle(self, *args, **options):
        ensure_default_groups()

        cursos_data = [
            ("1ro", "1ra", Curso.DIVISION_CB, Curso.TURNO_TM),
            ("1ro", "2da", Curso.DIVISION_CB, Curso.TURNO_TM),
            ("2do", "1ra", Curso.DIVISION_CB, Curso.TURNO_TM),
            ("2do", "2da", Curso.DIVISION_CB, Curso.TURNO_TM),
            ("3ro", "1ra", Curso.DIVISION_CB, Curso.TURNO_TM),
            ("3ro", "2da", Curso.DIVISION_CB, Curso.TURNO_TM),
            ("4to", "1ra", Curso.DIVISION_CS, Curso.TURNO_TM),
            ("4to", "2da", Curso.DIVISION_CS, Curso.TURNO_TM),
            ("5to", "1ra", Curso.DIVISION_CS, Curso.TURNO_TM),
            ("5to", "2da", Curso.DIVISION_CS, Curso.TURNO_TM),
            ("6to", "1ra", Curso.DIVISION_CS, Curso.TURNO_TM),
            ("6to", "2da", Curso.DIVISION_CS, Curso.TURNO_TM),
        ]
        for anio, curso, division, turno in cursos_data:
            Curso.objects.get_or_create(
                anio=anio,
                curso=curso,
                division=division,
                turno=turno,
                defaults={"activo": True},
            )

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

        beneficios = [
            ("Descuento en fotocopias", "Acceso a descuentos para estudiantes y familias."),
            ("Acompañamiento escolar", "Beneficios y apoyo en materiales para el cursado."),
            ("Promociones con comercios", "Acuerdos con librerías y comercios de la comunidad."),
        ]
        for orden, (titulo, descripcion) in enumerate(beneficios, start=1):
            Beneficio.objects.get_or_create(
                titulo=titulo,
                defaults={"descripcion": descripcion, "activo": True, "orden": orden},
            )

        libreria, _ = ActividadComercial.objects.get_or_create(nombre="Librería")
        papeleria, _ = ActividadComercial.objects.get_or_create(nombre="Papelería")

        Comercio.objects.get_or_create(
            nombre="Librería Sur",
            defaults={
                "actividad_comercial": libreria,
                "propietario": "Marina López",
                "beneficio_texto": "10% en útiles escolares",
                "estado": Comercio.ESTADO_FIRMADO,
                "fecha_convenio": date(2026, 3, 30),
                "flyer_disponible": True,
                "telefono": "2944-000111",
                "direccion": "Mitre 123",
                "ciudad": "General Roca",
                "provincia": "Río Negro",
                "url_presencia_web": "https://instagram.com/libreriasur",
            },
        )
        Comercio.objects.get_or_create(
            nombre="Papelera Centro",
            defaults={
                "actividad_comercial": papeleria,
                "propietario": "Juan Pérez",
                "beneficio_texto": "2x1 en anillados",
                "estado": Comercio.ESTADO_FIRMADO,
                "flyer_disponible": True,
                "telefono": "2944-000222",
                "direccion": "San Martín 55",
                "ciudad": "General Roca",
                "provincia": "Río Negro",
                "url_presencia_web": "https://papeleracentro.example.com",
            },
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
