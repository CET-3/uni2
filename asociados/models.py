import uuid

from django.conf import settings
from django.db import models
from django.db.models import Max


class Colegio(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    direccion = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Colegio"
        verbose_name_plural = "Colegios"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Curso(models.Model):
    colegio = models.ForeignKey(Colegio, on_delete=models.PROTECT, related_name="cursos")
    nombre = models.CharField(max_length=50)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
        ordering = ["colegio__nombre", "nombre"]
        constraints = [
            models.UniqueConstraint(fields=["colegio", "nombre"], name="uniq_curso_por_colegio")
        ]
        indexes = [models.Index(fields=["colegio", "activo"])]

    def __str__(self):
        return f"{self.colegio} - {self.nombre}"


class Asociado(models.Model):
    TIPO_ASOCIADO = "asociado"
    TIPO_ADHERENTE = "adherente"
    TIPOS = [
        (TIPO_ASOCIADO, "Asociado"),
        (TIPO_ADHERENTE, "Adherente"),
    ]

    ESTADO_ACTIVO = "activo"
    ESTADO_INACTIVO = "inactivo"
    ESTADO_EGRESADO = "egresado"
    ESTADOS = [
        (ESTADO_ACTIVO, "Activo"),
        (ESTADO_INACTIVO, "Inactivo"),
        (ESTADO_EGRESADO, "Egresado"),
    ]

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="asociado",
        blank=True,
        null=True,
    )
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    numero_asociado = models.PositiveIntegerField(unique=True, blank=True, null=True)
    token_credencial = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    curso_actual = models.ForeignKey(
        "asociados.Curso",
        on_delete=models.SET_NULL,
        related_name="asociados_actuales",
        blank=True,
        null=True,
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default=ESTADO_ACTIVO)
    fecha_alta = models.DateField()
    fecha_inicio_cobro = models.DateField()
    fecha_baja = models.DateField(blank=True, null=True)
    motivo_baja = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Asociado"
        verbose_name_plural = "Asociados"
        ordering = ["apellido", "nombre"]
        indexes = [
            models.Index(fields=["estado", "tipo"]),
            models.Index(fields=["numero_asociado"]),
            models.Index(fields=["fecha_inicio_cobro"]),
        ]

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"

    @classmethod
    def next_numero_asociado(cls) -> int:
        ultimo = cls.objects.aggregate(ultimo=Max("numero_asociado"))["ultimo"] or 0
        return ultimo + 1

    def save(self, *args, **kwargs):
        if self.numero_asociado is None:
            self.numero_asociado = self.next_numero_asociado()
        super().save(*args, **kwargs)


class InscripcionCurso(models.Model):
    asociado = models.ForeignKey(Asociado, on_delete=models.CASCADE, related_name="inscripciones")
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT, related_name="inscripciones")
    ciclo_lectivo = models.PositiveIntegerField()
    activa = models.BooleanField(default=True)
    fecha_desde = models.DateField()
    fecha_hasta = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = "Inscripcion a curso"
        verbose_name_plural = "Inscripciones a curso"
        ordering = ["-ciclo_lectivo", "-fecha_desde"]
        constraints = [
            models.UniqueConstraint(
                fields=["asociado", "curso", "ciclo_lectivo", "fecha_desde"],
                name="uniq_inscripcion_historial",
            )
        ]
        indexes = [
            models.Index(fields=["asociado", "activa"]),
            models.Index(fields=["ciclo_lectivo"]),
        ]

    def __str__(self):
        return f"{self.asociado} - {self.curso} ({self.ciclo_lectivo})"
