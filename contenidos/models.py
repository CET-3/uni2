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


class Servicio(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    precio_referencia = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre


class Publicidad(models.Model):
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to="publicidades/", blank=True)
    link = models.URLField(blank=True)
    activo = models.BooleanField(default=True)
    fecha_desde = models.DateField(blank=True, null=True)
    fecha_hasta = models.DateField(blank=True, null=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Publicidad"
        verbose_name_plural = "Publicidades"
        ordering = ["orden", "titulo"]

    def __str__(self):
        return self.titulo


class HorarioAtencion(models.Model):
    DIAS_SEMANA = [
        (1, "Lunes"),
        (2, "Martes"),
        (3, "Miercoles"),
        (4, "Jueves"),
        (5, "Viernes"),
        (6, "Sabado"),
        (7, "Domingo"),
    ]

    dia_semana = models.PositiveSmallIntegerField(choices=DIAS_SEMANA)
    hora_desde = models.TimeField()
    hora_hasta = models.TimeField()
    descripcion = models.CharField(max_length=255, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Horario de atencion"
        verbose_name_plural = "Horarios de atencion"
        ordering = ["dia_semana", "hora_desde"]

    def __str__(self):
        return f"{self.get_dia_semana_display()} {self.hora_desde}-{self.hora_hasta}"

