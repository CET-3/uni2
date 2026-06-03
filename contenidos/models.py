from django.db import models


class Beneficio(models.Model):
    titulo = models.CharField(
        "título",
        max_length=150,
        help_text="Nombre visible del beneficio.",
    )
    descripcion = models.TextField(
        "descripción",
        help_text="Texto público que explica el beneficio.",
    )
    activo = models.BooleanField(
        "activo",
        default=True,
        help_text="Indica si el beneficio se publica en el sitio.",
    )
    orden = models.PositiveIntegerField(
        "orden",
        default=0,
        help_text="Posición usada para ordenar los beneficios publicados.",
    )

    class Meta:
        verbose_name = "Beneficio"
        verbose_name_plural = "Beneficios"
        ordering = ["orden", "titulo"]

    def __str__(self):
        return self.titulo
