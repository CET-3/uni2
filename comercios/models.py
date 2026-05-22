from django.conf import settings
from django.db import models


class Comercio(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="comercio",
        blank=True,
        null=True,
    )
    nombre = models.CharField(max_length=150)
    responsable = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    direccion = models.CharField(max_length=255)
    url_presencia_web = models.URLField(blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    provincia = models.CharField(max_length=100, blank=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Comercio"
        verbose_name_plural = "Comercios"
        ordering = ["nombre"]
        indexes = [models.Index(fields=["activo", "nombre"])]

    def __str__(self):
        return self.nombre


class BeneficioComercio(models.Model):
    TIPO_PORCENTAJE = "porcentaje"
    TIPO_MONTO_FIJO = "monto_fijo"
    TIPO_PROMOCION = "promocion"
    TIPO_OTRO = "otro"
    TIPOS_DESCUENTO = [
        (TIPO_PORCENTAJE, "Porcentaje"),
        (TIPO_MONTO_FIJO, "Monto fijo"),
        (TIPO_PROMOCION, "Promocion"),
        (TIPO_OTRO, "Otro"),
    ]

    comercio = models.ForeignKey(Comercio, on_delete=models.CASCADE, related_name="beneficios")
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    tipo_descuento = models.CharField(max_length=20, choices=TIPOS_DESCUENTO)
    valor_descuento = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    condiciones = models.TextField(blank=True)
    fecha_desde = models.DateField(blank=True, null=True)
    fecha_hasta = models.DateField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Beneficio de comercio"
        verbose_name_plural = "Beneficios de comercio"
        ordering = ["comercio__nombre", "titulo"]
        indexes = [
            models.Index(fields=["comercio", "activo"]),
            models.Index(fields=["fecha_desde", "fecha_hasta"]),
        ]

    def __str__(self):
        return f"{self.comercio} - {self.titulo}"
