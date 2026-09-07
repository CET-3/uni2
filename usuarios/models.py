from django.conf import settings
from django.db import models


class Notificacion(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notificaciones",
    )
    titulo = models.CharField(max_length=150)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_creacion"]
        verbose_name = "Notificacion"
        verbose_name_plural = "Notificaciones"
        indexes = [
            models.Index(fields=["usuario", "leida"]),
            models.Index(fields=["fecha_creacion"]),
        ]

    def __str__(self):
        return f"{self.titulo} - {self.usuario}"


class EstadoDatosStaging(models.Model):
    CLAVE_ACTUAL = "actual"

    clave = models.CharField(
        "clave",
        max_length=20,
        primary_key=True,
        default=CLAVE_ACTUAL,
        editable=False,
        help_text="Identificador único del estado habilitado para staging.",
    )
    refresh_id = models.CharField(
        "identificador del refresco",
        max_length=64,
        help_text="Debe coincidir con el epoch privado publicado por la PWA.",
    )
    listo_desde = models.DateTimeField(
        "listo desde",
        help_text="Momento en que terminó el endurecimiento completo de la copia.",
    )

    class Meta:
        verbose_name = "estado de datos de staging"
        verbose_name_plural = "estados de datos de staging"

    def __str__(self):
        return f"Staging listo: {self.refresh_id}"
