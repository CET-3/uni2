import uuid

from django.conf import settings
from django.db import models
from django.db.models import Max


class CicloLectivo(models.Model):
    anio = models.PositiveSmallIntegerField(
        "año",
        unique=True,
        help_text="Año del ciclo lectivo.",
    )

    class Meta:
        verbose_name = "Ciclo lectivo"
        verbose_name_plural = "Ciclos lectivos"
        ordering = ["-anio"]

    def __str__(self):
        return str(self.anio)


class Colegio(models.Model):
    nombre = models.CharField(
        "nombre",
        max_length=150,
        unique=True,
        help_text="Nombre de la institución educativa.",
    )
    direccion = models.CharField(
        "dirección",
        max_length=255,
        blank=True,
        null=True,
        help_text="Dirección física del colegio.",
    )
    telefono = models.CharField(
        "teléfono",
        max_length=50,
        blank=True,
        null=True,
        help_text="Teléfono de contacto del colegio.",
    )
    email = models.EmailField(
        "email",
        blank=True,
        null=True,
        help_text="Correo de contacto del colegio.",
    )
    activo = models.BooleanField(
        "activo",
        default=True,
        help_text="Indica si el colegio participa activamente en el sistema.",
    )

    class Meta:
        verbose_name = "Colegio"
        verbose_name_plural = "Colegios"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Curso(models.Model):
    colegio = models.ForeignKey(
        Colegio,
        on_delete=models.PROTECT,
        related_name="cursos",
        verbose_name="colegio",
        help_text="Colegio al que pertenece el curso.",
    )
    nombre = models.CharField(
        "nombre",
        max_length=50,
        help_text="Nombre del curso, por ejemplo: 1° 1°.",
    )
    activo = models.BooleanField(
        "activo",
        default=True,
        help_text="Indica si el curso está activo en el sistema.",
    )

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
    asociado = models.ForeignKey(
        Asociado,
        on_delete=models.CASCADE,
        related_name="inscripciones",
        verbose_name="asociado",
        help_text="Asociado inscripto en el curso.",
    )
    curso = models.ForeignKey(
        Curso,
        on_delete=models.PROTECT,
        related_name="inscripciones",
        verbose_name="curso",
        help_text="Curso en el que está inscripto el asociado.",
    )
    ciclo_lectivo = models.ForeignKey(
        CicloLectivo,
        on_delete=models.PROTECT,
        related_name="inscripciones",
        verbose_name="ciclo lectivo",
        help_text="Año lectivo de esta inscripción.",
    )
    activa = models.BooleanField(
        "activa",
        default=True,
        help_text="Indica si esta es la inscripción vigente del asociado.",
    )
    fecha_desde = models.DateField(
        "fecha desde",
        help_text="Fecha de inicio de esta inscripción.",
    )
    fecha_hasta = models.DateField(
        "fecha hasta",
        blank=True,
        null=True,
        help_text="Fecha de fin de esta inscripción. Vacío si sigue activa.",
    )

    class Meta:
        verbose_name = "Inscripción a curso"
        verbose_name_plural = "Inscripciones a curso"
        ordering = ["-ciclo_lectivo__anio", "-fecha_desde"]
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
