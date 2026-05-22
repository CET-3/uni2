from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from asociados.models import Colegio, Curso
from comercios.models import BeneficioComercio, Comercio
from contenidos.models import Beneficio, HorarioAtencion, Publicidad, Servicio
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

        beneficios = [
            ("Descuento en fotocopias", "Acceso a descuentos para estudiantes y familias."),
            ("Acompanamiento escolar", "Beneficios y apoyo en materiales para el cursado."),
            ("Promociones con comercios", "Acuerdos con librerias y servicios de la comunidad."),
        ]
        for orden, (titulo, descripcion) in enumerate(beneficios, start=1):
            Beneficio.objects.get_or_create(
                titulo=titulo,
                defaults={"descripcion": descripcion, "activo": True, "orden": orden},
            )

        servicios = [
            ("Cuadernillos", "Materiales de apoyo y cuadernillos de trabajo.", 3500),
            ("Apuntes", "Apuntes y resumentes para materias troncales.", 2500),
            ("Fotocopias", "Servicio de impresion y fotocopias para estudiantes.", 1000),
        ]
        for orden, (nombre, descripcion, precio) in enumerate(servicios, start=1):
            Servicio.objects.get_or_create(
                nombre=nombre,
                defaults={
                    "descripcion": descripcion,
                    "precio_referencia": precio,
                    "activo": True,
                    "orden": orden,
                },
            )

        horarios = [
            (1, "08:00", "12:00", "Atencion administrativa"),
            (3, "14:00", "18:00", "Atencion a asociados"),
            (5, "08:00", "12:00", "Consultas y pagos"),
        ]
        for dia_semana, hora_desde, hora_hasta, descripcion in horarios:
            HorarioAtencion.objects.get_or_create(
                dia_semana=dia_semana,
                hora_desde=hora_desde,
                hora_hasta=hora_hasta,
                defaults={"descripcion": descripcion, "activo": True},
            )

        publicidades = [
            (
                "Bienvenidos a Uni2",
                "La mutual escolar ya cuenta con una plataforma para asociados y comercios.",
                1,
            ),
            (
                "Beneficios activos",
                "Consulta descuentos y servicios disponibles para la comunidad educativa.",
                2,
            ),
        ]
        for titulo, descripcion, orden in publicidades:
            Publicidad.objects.get_or_create(
                titulo=titulo,
                defaults={"descripcion": descripcion, "activo": True, "orden": orden},
            )

        comercio_1, _ = Comercio.objects.get_or_create(
            nombre="Libreria Sur",
            defaults={
                "responsable": "Marina Lopez",
                "telefono": "2944-000111",
                "direccion": "Mitre 123",
                "ciudad": "General Roca",
                "provincia": "Rio Negro",
                "url_presencia_web": "https://instagram.com/libreriasur",
                "activo": True,
            },
        )
        comercio_2, _ = Comercio.objects.get_or_create(
            nombre="Papelera Centro",
            defaults={
                "responsable": "Juan Perez",
                "telefono": "2944-000222",
                "direccion": "San Martin 55",
                "ciudad": "General Roca",
                "provincia": "Rio Negro",
                "url_presencia_web": "https://papeleracentro.example.com",
                "activo": True,
            },
        )

        BeneficioComercio.objects.get_or_create(
            comercio=comercio_1,
            titulo="10% en utiles escolares",
            defaults={
                "descripcion": "Descuento para asociados en utiles seleccionados.",
                "tipo_descuento": BeneficioComercio.TIPO_PORCENTAJE,
                "valor_descuento": 10,
                "condiciones": "Presentar credencial digital vigente.",
                "activo": True,
            },
        )
        BeneficioComercio.objects.get_or_create(
            comercio=comercio_2,
            titulo="2x1 en anillados",
            defaults={
                "descripcion": "Promocion especial para asociados.",
                "tipo_descuento": BeneficioComercio.TIPO_PROMOCION,
                "condiciones": "Valido de lunes a viernes.",
                "activo": True,
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
