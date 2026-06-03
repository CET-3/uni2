from django.conf import settings
from django.db import models


class ActividadComercial(models.Model):
    nombre = models.CharField(
        "nombre",
        max_length=100,
        unique=True,
        help_text="Nombre del rubro o actividad principal del comercio.",
    )

    class Meta:
        verbose_name = "Actividad comercial"
        verbose_name_plural = "Actividades comerciales"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Comercio(models.Model):
    ESTADO_PENDIENTE = "pendiente"
    ESTADO_FIRMADO = "firmado"
    ESTADO_VENCIDO = "vencido"
    ESTADO_BAJA = "baja"
    ESTADOS = [
        (ESTADO_PENDIENTE, "Pendiente"),
        (ESTADO_FIRMADO, "Firmado"),
        (ESTADO_VENCIDO, "Vencido"),
        (ESTADO_BAJA, "Baja"),
    ]

    actividad_comercial = models.ForeignKey(
        ActividadComercial,
        on_delete=models.PROTECT,
        related_name="comercios",
        verbose_name="actividad comercial",
        help_text="Rubro o actividad principal del comercio.",
    )
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="comercio",
        blank=True,
        null=True,
        verbose_name="usuario",
        help_text="Usuario que puede iniciar sesión como este comercio.",
    )
    nombre = models.CharField(
        "nombre",
        max_length=150,
        help_text="Nombre público del comercio adherido.",
    )
    propietario = models.CharField(
        "propietario",
        max_length=150,
        blank=True,
        null=True,
        help_text="Nombre de la persona propietaria o referente del comercio.",
    )
    beneficio_texto = models.TextField(
        "beneficio",
        help_text="Texto público que describe el beneficio vigente del comercio.",
    )
    estado = models.CharField(
        "estado",
        max_length=20,
        choices=ESTADOS,
        default=ESTADO_PENDIENTE,
        help_text="Estado del convenio con el comercio.",
    )
    fecha_convenio = models.DateField(
        "fecha de convenio",
        blank=True,
        null=True,
        help_text="Fecha en que se firmó o registró el convenio.",
    )
    notas = models.TextField(
        "notas",
        blank=True,
        null=True,
        help_text="Notas internas para seguimiento administrativo.",
    )
    flyer_disponible = models.BooleanField(
        "flyer disponible",
        default=False,
        help_text="Indica si existe un flyer o pieza de difusión disponible.",
    )
    email = models.EmailField(
        "email",
        blank=True,
        null=True,
        help_text="Correo público o de contacto del comercio.",
    )
    telefono = models.CharField(
        "teléfono",
        max_length=50,
        blank=True,
        null=True,
        help_text="Teléfono público o de contacto del comercio.",
    )
    direccion = models.CharField(
        "dirección",
        max_length=255,
        help_text="Dirección física del comercio.",
    )
    url_presencia_web = models.URLField(
        "presencia web",
        blank=True,
        null=True,
        help_text="URL pública del sitio, red social o presencia web del comercio.",
    )
    ciudad = models.CharField(
        "ciudad",
        max_length=100,
        blank=True,
        null=True,
        help_text="Ciudad donde se encuentra el comercio.",
    )
    provincia = models.CharField(
        "provincia",
        max_length=100,
        blank=True,
        null=True,
        help_text="Provincia donde se encuentra el comercio.",
    )
    latitud = models.DecimalField(
        "latitud",
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        help_text="Coordenada de latitud para uso futuro en mapa.",
    )
    longitud = models.DecimalField(
        "longitud",
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        help_text="Coordenada de longitud para uso futuro en mapa.",
    )

    class Meta:
        verbose_name = "Comercio"
        verbose_name_plural = "Comercios"
        ordering = ["nombre"]
        indexes = [models.Index(fields=["estado", "nombre"])]

    def __str__(self):
        return self.nombre
