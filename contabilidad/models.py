from decimal import Decimal

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum


class CuentaContable(models.Model):
    TIPO_ACTIVO = "activo"
    TIPO_PASIVO = "pasivo"
    TIPO_PATRIMONIO = "patrimonio"
    TIPO_INGRESO = "ingreso"
    TIPO_EGRESO = "egreso"
    TIPOS = [
        (TIPO_ACTIVO, "Activo"),
        (TIPO_PASIVO, "Pasivo"),
        (TIPO_PATRIMONIO, "Patrimonio"),
        (TIPO_INGRESO, "Ingreso"),
        (TIPO_EGRESO, "Egreso"),
    ]

    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=150, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Cuenta contable"
        verbose_name_plural = "Cuentas contables"
        ordering = ["codigo", "nombre"]
        indexes = [models.Index(fields=["tipo", "activa"])]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Asiento(models.Model):
    TIPO_INGRESO = "ingreso"
    TIPO_EGRESO = "egreso"
    TIPOS = [
        (TIPO_INGRESO, "Ingreso"),
        (TIPO_EGRESO, "Egreso"),
    ]

    fecha = models.DateField()
    descripcion = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    importe = models.DecimalField(max_digits=10, decimal_places=2)
    origen_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        related_name="asientos",
        blank=True,
        null=True,
    )
    origen_object_id = models.PositiveBigIntegerField(blank=True, null=True)
    origen = GenericForeignKey("origen_content_type", "origen_object_id")

    class Meta:
        verbose_name = "Asiento"
        verbose_name_plural = "Asientos"
        ordering = ["-fecha", "-id"]
        indexes = [
            models.Index(fields=["fecha", "tipo"]),
            models.Index(fields=["origen_content_type", "origen_object_id"]),
        ]

    def __str__(self):
        return f"{self.tipo} - {self.descripcion}"

    def get_totales_partidas(self):
        totales = self.partidas.values("movimiento").annotate(total=Sum("importe"))
        debe = sum(
            (item["total"] for item in totales if item["movimiento"] == PartidaAsiento.MOVIMIENTO_DEBE),
            start=Decimal("0"),
        )
        haber = sum(
            (item["total"] for item in totales if item["movimiento"] == PartidaAsiento.MOVIMIENTO_HABER),
            start=Decimal("0"),
        )
        return debe, haber

    def validate_partidas_balanceadas(self):
        cantidad = self.partidas.count()
        if cantidad < 2:
            raise ValidationError("El asiento debe tener al menos 2 partidas.")

        debe, haber = self.get_totales_partidas()
        if debe != haber:
            raise ValidationError("El asiento debe estar balanceado: debe y haber deben coincidir.")

        if self.importe != debe:
            raise ValidationError("El importe del asiento debe coincidir con el total del debe y del haber.")


class PartidaAsiento(models.Model):
    MOVIMIENTO_DEBE = "debe"
    MOVIMIENTO_HABER = "haber"
    MOVIMIENTOS = [
        (MOVIMIENTO_DEBE, "Debe"),
        (MOVIMIENTO_HABER, "Haber"),
    ]

    asiento = models.ForeignKey(Asiento, on_delete=models.CASCADE, related_name="partidas")
    cuenta = models.ForeignKey(CuentaContable, on_delete=models.PROTECT, related_name="partidas")
    movimiento = models.CharField(max_length=10, choices=MOVIMIENTOS)
    importe = models.DecimalField(max_digits=10, decimal_places=2)
    detalle = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Partida de asiento"
        verbose_name_plural = "Partidas de asiento"
        ordering = ["id"]
        indexes = [
            models.Index(fields=["asiento", "movimiento"]),
            models.Index(fields=["cuenta"]),
        ]

    def __str__(self):
        return f"{self.asiento} - {self.cuenta} - {self.movimiento}"
