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
    )
    nombre = models.CharField(max_length=150)
    propietario = models.CharField(max_length=150, blank=True)
    beneficio_texto = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default=ESTADO_PENDIENTE)
    fecha_convenio = models.DateField(blank=True, null=True)
    notas = models.TextField(blank=True)
    flyer_disponible = models.BooleanField(default=False)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    direccion = models.CharField(max_length=255)
    url_presencia_web = models.URLField(blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    provincia = models.CharField(max_length=100, blank=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    class Meta:
        verbose_name = "Comercio"
        verbose_name_plural = "Comercios"
        ordering = ["nombre"]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(beneficio_texto=""),
                name="comercio_beneficio_texto_no_vacio",
            )
        ]
        indexes = [models.Index(fields=["estado", "nombre"])]

    def __str__(self):
        return self.nombre
