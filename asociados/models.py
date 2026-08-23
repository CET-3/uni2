import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
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


class Curso(models.Model):
    DIVISION_CB = "CB"
    DIVISION_CS = "CS"
    DIVISIONES = [
        (DIVISION_CB, "Ciclo Básico"),
        (DIVISION_CS, "Ciclo Superior"),
    ]

    TURNO_TM = "TM"
    TURNO_TT = "TT"
    TURNOS = [
        (TURNO_TM, "Turno Mañana"),
        (TURNO_TT, "Turno Tarde"),
    ]
    anio = models.CharField(
        "año",
        max_length=10,
        help_text="Año que cursa, ej: 1ro, 2do, 3ro.",
    )
    curso = models.CharField(
        "curso",
        max_length=10,
        help_text="División o número de curso, ej: 1ra, 2da, única.",
    )
    division = models.CharField(
        "división",
        max_length=2,
        choices=DIVISIONES,
        default=DIVISION_CB,
        help_text="Ciclo al que pertenece: CB (Ciclo Básico) o CS (Ciclo Superior).",
    )
    turno = models.CharField(
        "turno",
        max_length=2,
        choices=TURNOS,
        default=TURNO_TM,
        help_text="Turno: TM (Turno Mañana) o TT (Turno Tarde).",
    )
    activo = models.BooleanField(
        "activo",
        default=True,
        help_text="Indica si el curso está activo en el sistema.",
    )

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
        ordering = ["division", "anio", "curso", "turno"]
        constraints = [
            models.UniqueConstraint(fields=["anio", "curso", "division", "turno"], name="uniq_curso")
        ]
        indexes = []

    def __str__(self):
        return f"{self.anio} {self.curso} {self.division} {self.turno}"


class ClasificacionAdherente(models.Model):
    NOMBRE_SIN_CLASIFICAR = "Sin clasificar"

    nombre = models.CharField(
        "nombre",
        max_length=100,
        unique=True,
        help_text="Nombre visible de la clasificación del adherente.",
    )
    activa = models.BooleanField(
        "activa",
        default=True,
        help_text="Indica si puede asignarse en nuevas altas y ediciones.",
    )
    orden = models.PositiveIntegerField(
        "orden",
        default=0,
        help_text="Posición en formularios y listados.",
    )

    class Meta:
        verbose_name = "Clasificación de adherente"
        verbose_name_plural = "Clasificaciones de adherentes"
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre


class Asociado(models.Model):
    TIPO_ASOCIADO = "asociado"
    TIPO_ADHERENTE = "adherente"
    TIPOS = [
        (TIPO_ASOCIADO, "Asociado"),
        (TIPO_ADHERENTE, "Adherente"),
    ]

    ESTADO_ACTIVO = "activo"
    ESTADO_INACTIVO = "inactivo"
    ESTADOS = [
        (ESTADO_ACTIVO, "Activo"),
        (ESTADO_INACTIVO, "Inactivo"),
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
    direccion = models.CharField(
        "dirección",
        max_length=255,
        blank=True,
        help_text="Domicilio del asociado.",
    )
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
    clasificacion_adherente = models.ForeignKey(
        ClasificacionAdherente,
        on_delete=models.PROTECT,
        related_name="adherentes",
        verbose_name="clasificación de adherente",
        blank=True,
        null=True,
        help_text="Clasificación institucional; corresponde únicamente a adherentes.",
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

    def get_dato_institucional(self):
        if self.tipo == self.TIPO_ASOCIADO:
            return "Curso", str(self.curso_actual) if self.curso_actual else ""
        return (
            "Clasificación",
            str(self.clasificacion_adherente) if self.clasificacion_adherente else "",
        )

    def clean(self):
        super().clean()
        errores = {}
        if self.tipo == self.TIPO_ASOCIADO:
            if self.curso_actual is None:
                errores["curso_actual"] = "Elegí un curso para el asociado."
            if self.clasificacion_adherente is not None:
                errores["clasificacion_adherente"] = "La clasificación corresponde únicamente a adherentes."
        elif self.tipo == self.TIPO_ADHERENTE:
            if self.clasificacion_adherente is None:
                errores["clasificacion_adherente"] = "Elegí una clasificación para el adherente."
            if self.curso_actual is not None:
                errores["curso_actual"] = "El adherente no puede tener un curso actual."
        if errores:
            raise ValidationError(errores)

    @classmethod
    def next_numero_asociado(cls) -> int:
        ultimo = cls.objects.aggregate(ultimo=Max("numero_asociado"))["ultimo"] or 0
        return ultimo + 1

    def save(self, *args, **kwargs):
        if self.numero_asociado is None:
            self.numero_asociado = self.next_numero_asociado()
        super().save(*args, **kwargs)
