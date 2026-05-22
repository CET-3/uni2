from decimal import Decimal

from django.conf import settings
from django.db import models

from asociados.models import Asociado


class PeriodoCuota(models.Model):
    mes = models.PositiveSmallIntegerField()
    anio = models.PositiveSmallIntegerField()
    importe = models.DecimalField(max_digits=10, decimal_places=2)
    importe_recargo_mora = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_vencimiento = models.DateField()
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Periodo de cuota"
        verbose_name_plural = "Periodos de cuota"
        ordering = ["-anio", "-mes"]
        constraints = [
            models.UniqueConstraint(fields=["mes", "anio"], name="uniq_periodo_mes_anio")
        ]
        indexes = [models.Index(fields=["anio", "mes"])]

    def __str__(self):
        return f"{self.mes:02d}/{self.anio}"


class Cuota(models.Model):
    ESTADO_PENDIENTE = "pendiente"
    ESTADO_PARCIAL = "parcial"
    ESTADO_PAGADA = "pagada"
    ESTADO_VENCIDA = "vencida"
    ESTADO_BONIFICADA = "bonificada"
    ESTADOS = [
        (ESTADO_PENDIENTE, "Pendiente"),
        (ESTADO_PARCIAL, "Parcial"),
        (ESTADO_PAGADA, "Pagada"),
        (ESTADO_VENCIDA, "Vencida"),
        (ESTADO_BONIFICADA, "Bonificada"),
    ]

    asociado = models.ForeignKey(Asociado, on_delete=models.CASCADE, related_name="cuotas")
    periodo = models.ForeignKey(PeriodoCuota, on_delete=models.PROTECT, related_name="cuotas")
    importe = models.DecimalField(max_digits=10, decimal_places=2)
    importe_recargo_mora = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    importe_pagado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default=ESTADO_PENDIENTE)
    fecha_generacion = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Cuota"
        verbose_name_plural = "Cuotas"
        ordering = ["periodo__anio", "periodo__mes"]
        constraints = [
            models.UniqueConstraint(fields=["asociado", "periodo"], name="uniq_cuota_asociado_periodo")
        ]
        indexes = [
            models.Index(fields=["asociado", "estado"]),
            models.Index(fields=["periodo"]),
        ]

    def __str__(self):
        return f"{self.asociado} - {self.periodo}"

    def get_importe_total_base(self) -> Decimal:
        return Decimal(str(self.importe))

    def get_importe_total_con_mora(self) -> Decimal:
        return self.get_importe_total_base() + Decimal(str(self.importe_recargo_mora))

    def paga_mora(self, fecha_referencia) -> bool:
        if fecha_referencia <= self.periodo.fecha_vencimiento:
            return False
        pagado_al_vencimiento = (
            self.aplicaciones.filter(pago__fecha__lte=self.periodo.fecha_vencimiento).aggregate(
                total=models.Sum("importe")
            )["total"]
            or Decimal("0")
        )
        return pagado_al_vencimiento < self.get_importe_total_base()

    def get_total_exigible(self, fecha_referencia) -> Decimal:
        if self.paga_mora(fecha_referencia):
            return self.get_importe_total_con_mora()
        return self.get_importe_total_base()

    def get_saldo_pendiente(self, fecha_referencia) -> Decimal:
        saldo = self.get_total_exigible(fecha_referencia) - Decimal(str(self.importe_pagado))
        return max(saldo, Decimal("0"))


class Pago(models.Model):
    METODO_EFECTIVO = "efectivo"
    METODO_BILLETERA = "billetera_virtual"
    METODOS = [
        (METODO_EFECTIVO, "Efectivo"),
        (METODO_BILLETERA, "Billetera virtual"),
    ]

    asociado = models.ForeignKey(Asociado, on_delete=models.CASCADE, related_name="pagos")
    fecha = models.DateField()
    importe = models.DecimalField(max_digits=10, decimal_places=2)
    metodo = models.CharField(max_length=30, choices=METODOS)
    observaciones = models.TextField(blank=True)
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="pagos_registrados",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ["-fecha", "-id"]
        indexes = [models.Index(fields=["asociado", "fecha"]), models.Index(fields=["metodo"])]

    def __str__(self):
        return f"Pago {self.id} - {self.asociado}"


class PagoCuota(models.Model):
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE, related_name="aplicaciones")
    cuota = models.ForeignKey(Cuota, on_delete=models.CASCADE, related_name="aplicaciones")
    importe = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Pago de cuota"
        verbose_name_plural = "Pagos de cuota"
        ordering = ["id"]
        indexes = [models.Index(fields=["pago"]), models.Index(fields=["cuota"])]

    def __str__(self):
        return f"{self.pago} -> {self.cuota}"
