from datetime import date

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError

from asociados.models import Asociado, Curso
from comercios.models import ActividadComercial, Comercio
from contenidos.models import CategoriaProductoServicio, ProductoServicio, Publicidad
from usuarios.roles import ADMINISTRADOR_APP_GROUP, PERMISOS_POR_GRUPO
from usuarios.services import (
    ADMIN_GROUP,
    ASOCIADO_GROUP,
    ATENCION_MUTUAL_GROUP,
    COMERCIO_GROUP,
    ensure_default_groups,
)


class Command(BaseCommand):
    help = "Carga datos ficticios para desarrollo local de Uni2."

    def handle(self, *args, **options):
        if not settings.ALLOW_DEMO_DATA:
            raise CommandError(
                "carga_inicial sólo está habilitado en desarrollo local y tests; "
                "no debe ejecutarse sobre producción."
            )

        ensure_default_groups()
        permisos_disponibles = {
            f"{permiso.content_type.app_label}.{permiso.codename}": permiso
            for permiso in Permission.objects.select_related("content_type")
        }
        for nombre_grupo, permisos in PERMISOS_POR_GRUPO.items():
            Group.objects.get(name=nombre_grupo).permissions.set(
                permisos_disponibles[permiso]
                for permiso in permisos
                if permiso in permisos_disponibles
            )

        # El grupo identifica a los superusuarios técnicos. is_superuser sigue
        # siendo la autoridad real y no se obtiene por pertenecer al grupo.
        Group.objects.get(name=ADMINISTRADOR_APP_GROUP).permissions.clear()

        # Cursos
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

        # ── Servicios (CategoriaProductoServicio + ProductoServicio) ──

        fotocopias, _ = CategoriaProductoServicio.objects.get_or_create(
            nombre="Fotocopias",
            defaults={
                "descripcion": "Servicios de impresión y fotocopiado para estudiantes y familias.",
                "etiqueta_icono": "printer",
                "texto_cta": "Consultá disponibilidad en la mutual o al uni2mutual@gmail.com",
                "activa": True,
                "orden": 1,
            },
        )
        ProductoServicio.objects.get_or_create(
            categoria=fotocopias,
            nombre="Fotocopia simple",
            defaults={
                "descripcion": "Fotocopia en blanco y negro.",
                "precio_asociados": 50,
                "precio_no_asociados": 80,
                "orden": 1,
            },
        )
        ProductoServicio.objects.get_or_create(
            categoria=fotocopias,
            nombre="Impresión color",
            defaults={
                "descripcion": "Impresión color tamaño A4.",
                "precio_asociados": 120,
                "precio_no_asociados": 180,
                "orden": 2,
            },
        )
        ProductoServicio.objects.get_or_create(
            categoria=fotocopias,
            nombre="Anillado",
            defaults={
                "descripcion": "Anillado de apuntes y trabajos prácticos.",
                "es_servicio": True,
                "precio_asociados": 600,
                "precio_no_asociados": 900,
                "orden": 3,
            },
        )

        uniformes, _ = CategoriaProductoServicio.objects.get_or_create(
            nombre="Uniformes",
            defaults={
                "descripcion": "Prendas y accesorios del uniforme escolar.",
                "etiqueta_icono": "tag",
                "texto_cta": "Consultá talles disponibles en la mutual.",
                "activa": True,
                "orden": 2,
            },
        )
        ProductoServicio.objects.get_or_create(
            categoria=uniformes,
            nombre="Campera polar",
            defaults={
                "descripcion": "Campera polar azul con logo bordado.",
                "precio_asociados": 8500,
                "precio_no_asociados": 10500,
                "orden": 1,
            },
        )
        ProductoServicio.objects.get_or_create(
            categoria=uniformes,
            nombre="Buzo",
            defaults={
                "descripcion": "Buzo de uniforme con capucha.",
                "precio_asociados": 7200,
                "precio_no_asociados": 9500,
                "orden": 2,
            },
        )

        bici, _ = CategoriaProductoServicio.objects.get_or_create(
            nombre="Bicicleta solidaria",
            defaults={
                "descripcion": "Programa de préstamo de bicicletas para estudiantes.",
                "etiqueta_icono": "bicycle",
                "texto_cta": "Inscribite en la mutual para usar el servicio.",
                "activa": True,
                "orden": 3,
            },
        )
        ProductoServicio.objects.get_or_create(
            categoria=bici,
            nombre="Préstamo de bicicleta",
            defaults={
                "descripcion": "Uso de bicicleta por el ciclo lectivo.",
                "es_servicio": True,
                "precio_asociados": 0,
                "precio_no_asociados": 0,
                "orden": 1,
            },
        )

        cuadernillos, _ = CategoriaProductoServicio.objects.get_or_create(
            nombre="Cuadernillos y anillado",
            defaults={
                "descripcion": "Cuadernillos armados por la mutual y servicio de anillado.",
                "etiqueta_icono": "book",
                "texto_cta": "Pedí presupuesto en la mutual.",
                "activa": True,
                "orden": 4,
            },
        )
        ProductoServicio.objects.get_or_create(
            categoria=cuadernillos,
            nombre="Cuadernillo A4",
            defaults={
                "descripcion": "Cuadernillo A4 con hojas rayadas, 48 hojas.",
                "precio_asociados": 400,
                "precio_no_asociados": 600,
                "orden": 1,
            },
        )
        ProductoServicio.objects.get_or_create(
            categoria=cuadernillos,
            nombre="Anillado profesional",
            defaults={
                "descripcion": "Anillado de trabajos prácticos y documentos.",
                "es_servicio": True,
                "precio_asociados": 500,
                "precio_no_asociados": 800,
                "orden": 2,
            },
        )

        # ── Actividades comerciales (rubros) ──

        gastronomia, _ = ActividadComercial.objects.get_or_create(
            nombre="Gastronomía",
            defaults={"descripcion": "Sabores y opciones para disfrutar en cada momento."},
        )
        act_fisica, _ = ActividadComercial.objects.get_or_create(
            nombre="Actividad física",
            defaults={"descripcion": "Espacios y propuestas para moverse, entrenar y sentirse bien."},
        )
        belleza, _ = ActividadComercial.objects.get_or_create(
            nombre="Belleza",
            defaults={"descripcion": "Servicios de cuidado personal y bienestar."},
        )
        vestimenta, _ = ActividadComercial.objects.get_or_create(
            nombre="Vestimenta",
            defaults={"descripcion": "Indumentaria y accesorios con beneficios para asociados."},
        )
        educacion, _ = ActividadComercial.objects.get_or_create(
            nombre="Educación",
            defaults={"descripcion": "Materiales y servicios para acompañar el aprendizaje."},
        )
        tecnologia, _ = ActividadComercial.objects.get_or_create(
            nombre="Tecnología y accesorios",
            defaults={"descripcion": "Tecnología, accesorios y soluciones para todos los días."},
        )

        # ── Comercios ──

        libreria_sur, _ = Comercio.objects.get_or_create(
            nombre="Librería Sur",
            defaults={
                "actividad_comercial": educacion,
                "descripcion": "Librería y artículos escolares para estudiantes y familias.",
                "propietario": "Marina López",
                "beneficio_texto": "10% en útiles escolares",
                "estado": Comercio.ESTADO_FIRMADO,
                "fecha_convenio": date(2026, 3, 30),
                "telefono": "2944-000111",
                "direccion": "Mitre 123",
                "ciudad": "General Roca",
                "provincia": "Río Negro",
                "url_presencia_web": "https://instagram.com/libreriasur",
            },
        )

        Comercio.objects.get_or_create(
            nombre="Alto Drugstore",
            defaults={
                "actividad_comercial": gastronomia,
                "descripcion": "Alimentos, bebidas y productos de uso diario.",
                "propietario": "Carlos Gómez",
                "beneficio_texto": "10% de descuento en compras al contado",
                "estado": Comercio.ESTADO_FIRMADO,
                "telefono": "2944-100111",
                "direccion": "San Martín 250",
                "ciudad": "General Roca",
                "provincia": "Río Negro",
            },
        )
        Comercio.objects.get_or_create(
            nombre="Librería Muñoz",
            defaults={
                "actividad_comercial": educacion,
                "descripcion": "Artículos de librería, útiles escolares y materiales de estudio.",
                "propietario": "Ana Muñoz",
                "beneficio_texto": "15% en todos los productos recibiendo Becas",
                "estado": Comercio.ESTADO_FIRMADO,
                "telefono": "2944-100222",
                "direccion": "Mitre 340",
                "ciudad": "General Roca",
                "provincia": "Río Negro",
            },
        )
        Comercio.objects.get_or_create(
            nombre="Atenas Gimnasio",
            defaults={
                "actividad_comercial": act_fisica,
                "descripcion": "Espacio de entrenamiento físico con clases y equipamiento.",
                "propietario": "María Atenas Covelli",
                "beneficio_texto": "1 clase gratis + 10% en cuotas",
                "estado": Comercio.ESTADO_FIRMADO,
                "telefono": "2944-100333",
                "direccion": "Belgrano 500",
                "ciudad": "General Roca",
                "provincia": "Río Negro",
            },
        )
        Comercio.objects.get_or_create(
            nombre="Andromeda Studio",
            defaults={
                "actividad_comercial": belleza,
                "descripcion": "Servicios de belleza, manicuría y peinados.",
                "propietario": "Luciana López",
                "beneficio_texto": "20% en manicuría y peinados",
                "estado": Comercio.ESTADO_FIRMADO,
                "telefono": "2944-100444",
                "direccion": "Rivadavia 150",
                "ciudad": "General Roca",
                "provincia": "Río Negro",
            },
        )
        Comercio.objects.get_or_create(
            nombre="Carolina's Closet",
            defaults={
                "actividad_comercial": vestimenta,
                "descripcion": "Indumentaria femenina urbana y formal.",
                "propietario": "Carolina Fernández",
                "beneficio_texto": "15% en indumentaria femenina",
                "estado": Comercio.ESTADO_FIRMADO,
                "telefono": "2944-100555",
                "direccion": "Mitre 420",
                "ciudad": "General Roca",
                "provincia": "Río Negro",
            },
        )
        Comercio.objects.get_or_create(
            nombre="Techno Store",
            defaults={
                "actividad_comercial": tecnologia,
                "descripcion": "Accesorios tecnológicos y asesoramiento especializado.",
                "propietario": "Pedro Martínez",
                "beneficio_texto": "10% en accesorios tecnológicos",
                "estado": Comercio.ESTADO_FIRMADO,
                "telefono": "2944-100666",
                "direccion": "San Martín 600",
                "ciudad": "General Roca",
                "provincia": "Río Negro",
            },
        )

        # ── Publicidades ──

        Publicidad.objects.get_or_create(
            titulo="Fotocopia simple desde $ 50,00",
            defaults={
                "descripcion": "Aprovechá el precio especial para asociados en todas las fotocopias.",
                "etiqueta_principal": "Servicio",
                "etiqueta_secundaria": "50% OFF",
                "producto_servicio": ProductoServicio.objects.get(nombre="Fotocopia simple"),
                "activa": True,
                "orden": 1,
            },
        )
        Publicidad.objects.get_or_create(
            titulo="Bicicleta solidaria",
            defaults={
                "descripcion": "Sumate al programa de préstamo gratuito de bicicletas.",
                "etiqueta_principal": "Programa",
                "etiqueta_secundaria": "Gratuito",
                "producto_servicio": ProductoServicio.objects.get(nombre="Préstamo de bicicleta"),
                "activa": True,
                "orden": 2,
            },
        )
        Publicidad.objects.get_or_create(
            titulo="10% OFF en Librería Sur",
            defaults={
                "descripcion": "Descuento exclusivo para asociados en útiles escolares.",
                "etiqueta_principal": "Comercio adherido",
                "etiqueta_secundaria": "10% OFF",
                "comercio": Comercio.objects.get(nombre="Librería Sur"),
                "activa": True,
                "orden": 3,
            },
        )

        # ── Usuarios ──

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
