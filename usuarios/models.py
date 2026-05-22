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

