from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from asociados.models import Asociado, Curso
from comercios.models import ActividadComercial, Comercio
from contenidos.models import Beneficio
from gestion.permissions import (
    GESTION_COBRAR_CUOTAS,
    GESTION_CONSULTAR_ASOCIADOS,
    GESTION_DASHBOARD,
    GESTION_EDITAR_ASOCIADOS,
    GESTION_PERMISSIONS,
)
from usuarios.services import (
    ADMIN_GROUP,
    ASOCIADO_GROUP,
    ATENCION_MUTUAL_GROUP,
    COMERCIO_GROUP,
    ensure_default_groups,
)


ATENCION_MUTUAL_PERMISSIONS = (
    GESTION_DASHBOARD,
    GESTION_CONSULTAR_ASOCIADOS,
    GESTION_EDITAR_ASOCIADOS,
    GESTION_COBRAR_CUOTAS,
)


class Command(BaseCommand):
    help = "Carga datos iniciales para desarrollo local de Uni2."

    def handle(self, *args, **options):
        ensure_default_groups()
        permisos_gestion = Permission.objects.filter(
            content_type__app_label="gestion",
            codename__in=[permission.split(".", 1)[1] for permission in GESTION_PERMISSIONS],
        )
        Group.objects.get(name=ADMIN_GROUP).permissions.add(*permisos_gestion)
        permisos_atencion = Permission.objects.filter(
            content_type__app_label="gestion",
            codename__in=[permission.split(".", 1)[1] for permission in ATENCION_MUTUAL_PERMISSIONS],
        )
        Group.objects.get(name=ATENCION_MUTUAL_GROUP).permissions.add(*permisos_atencion)

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

        libreria_sur, _ = Comercio.objects.get_or_create(
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

        curso_asociado = Curso.objects.get(anio="1ro", curso="1ra", division=Curso.DIVISION_CB, turno=Curso.TURNO_TM)

        atencion_user, created = user_model.objects.get_or_create(
            username="atencion",
            defaults={
                "email": "atencion@example.com",
                "first_name": "Atención",
                "last_name": "Mutual",
                "is_active": True,
            },
        )
        if created:
            atencion_user.set_password("atencion1234")
            atencion_user.save(update_fields=["password"])
        atencion_user.groups.add(Group.objects.get(name=ATENCION_MUTUAL_GROUP))
        atencion_user.groups.add(Group.objects.get(name=ASOCIADO_GROUP))

        atencion_asociado, _ = Asociado.objects.get_or_create(
            dni="40111223",
            defaults={
                "nombre": "Atención",
                "apellido": "Mutual",
                "tipo": Asociado.TIPO_ASOCIADO,
                "curso_actual": curso_asociado,
                "fecha_alta": date(2026, 3, 10),
                "fecha_inicio_cobro": date(2026, 3, 1),
                "email": "atencion@example.com",
                "telefono": "2944-000334",
                "direccion": "Mutual Escolar CET 3",
            },
        )
        if atencion_asociado.usuario_id is None and not hasattr(atencion_user, "asociado"):
            atencion_asociado.usuario = atencion_user
            atencion_asociado.save(update_fields=["usuario"])

        asociado_user, created = user_model.objects.get_or_create(
            username="asociado",
            defaults={
                "email": "asociado@example.com",
                "first_name": "Ana",
                "last_name": "Perez",
                "is_active": True,
            },
        )
        if created:
            asociado_user.set_password("asociado1234")
            asociado_user.save(update_fields=["password"])
        asociado_user.groups.add(Group.objects.get(name=ASOCIADO_GROUP))

        asociado, _ = Asociado.objects.get_or_create(
            dni="40111222",
            defaults={
                "nombre": "Ana",
                "apellido": "Perez",
                "tipo": Asociado.TIPO_ASOCIADO,
                "curso_actual": curso_asociado,
                "fecha_alta": date(2026, 3, 10),
                "fecha_inicio_cobro": date(2026, 3, 1),
                "email": "asociado@example.com",
                "telefono": "2944-000333",
                "direccion": "Calle Escuela 123",
            },
        )
        if asociado.usuario_id is None and not hasattr(asociado_user, "asociado"):
            asociado.usuario = asociado_user
            asociado.save(update_fields=["usuario"])

        comercio_user, created = user_model.objects.get_or_create(
            username="comercio",
            defaults={
                "email": "comercio@example.com",
                "first_name": "Marina",
                "last_name": "López",
                "is_active": True,
            },
        )
        if created:
            comercio_user.set_password("comercio1234")
            comercio_user.save(update_fields=["password"])
        comercio_user.groups.add(Group.objects.get(name=COMERCIO_GROUP))

        if libreria_sur.usuario_id is None and not hasattr(comercio_user, "comercio"):
            libreria_sur.usuario = comercio_user
            libreria_sur.save(update_fields=["usuario"])

        self.stdout.write(self.style.SUCCESS(f"Datos iniciales cargados al {date.today()}"))
