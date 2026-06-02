from django.db import models


class Beneficio(models.Model):
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Beneficio"
        verbose_name_plural = "Beneficios"
        ordering = ["orden", "titulo"]

    def __str__(self):
        return self.titulo
