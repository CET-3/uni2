from decimal import Decimal

from django.conf import settings
from django.db import models

from asociados.models import Asociado, CicloLectivo


class PeriodoCuota(models.Model):
    mes = models.PositiveSmallIntegerField(
        "mes",
        help_text="Mes del período (1 a 12).",
    )
    ciclo_lectivo = models.ForeignKey(
        CicloLectivo,
        on_delete=models.PROTECT,
        related_name="periodos_cuota",
        verbose_name="ciclo lectivo",
        help_text="Año lectivo al que corresponde este período.",
    )
    importe = models.DecimalField(
        "importe",
        max_digits=10,
        decimal_places=2,
        help_text="Importe base de la cuota para este período.",
    )
    importe_recargo_mes = models.DecimalField(
        "recargo por mora (mismo mes)",
        max_digits=10,
        decimal_places=2,
        default=Decimal("100.00"),
        help_text="Recargo fijo si se paga después del vencimiento pero dentro del mismo mes.",
    )
    importe_recargo_mes_siguiente = models.DecimalField(
        "recargo por mora (mes siguiente)",
        max_digits=10,
        decimal_places=2,
        default=Decimal("200.00"),
        help_text="Recargo fijo si se paga después de que pasó el mes de vencimiento.",
    )
    fecha_vencimiento = models.DateField(
        "fecha de vencimiento",
        help_text="Fecha límite para pagar sin recargo.",
    )
    activo = models.BooleanField(
        "activo",
        default=True,
        help_text="Indica si este período está activo para generar cuotas.",
    )

    class Meta:
        verbose_name = "Período de cuota"
        verbose_name_plural = "Períodos de cuota"
        ordering = ["-ciclo_lectivo__anio", "-mes"]
        constraints = [
            models.UniqueConstraint(fields=["mes", "ciclo_lectivo"], name="uniq_periodo_mes_ciclo")
        ]
        indexes = [models.Index(fields=["ciclo_lectivo", "mes"])]

    def __str__(self):
        return f"{self.mes:02d}/{self.ciclo_lectivo}"


class Cuota(models.Model):
    ESTADO_PENDIENTE = "pendiente"
    ESTADO_PAGADA = "pagada"
    ESTADO_VENCIDA = "vencida"
    ESTADOS = [
        (ESTADO_PENDIENTE, "Pendiente"),
        (ESTADO_PAGADA, "Pagada"),
        (ESTADO_VENCIDA, "Vencida"),
    ]

    asociado = models.ForeignKey(Asociado, on_delete=models.CASCADE, related_name="cuotas")
    periodo = models.ForeignKey(PeriodoCuota, on_delete=models.PROTECT, related_name="cuotas")
    importe = models.DecimalField(max_digits=10, decimal_places=2)
    importe_recargo_mes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    importe_recargo_mes_siguiente = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    importe_pagado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default=ESTADO_PENDIENTE)
    fecha_generacion = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Cuota"
        verbose_name_plural = "Cuotas"
        ordering = ["periodo__ciclo_lectivo__anio", "periodo__mes"]
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

    def get_recargo_aplicable(self, fecha_referencia) -> Decimal:
        if not self.paga_mora(fecha_referencia):
            return Decimal("0")
        if fecha_referencia.year == self.periodo.ciclo_lectivo.anio and fecha_referencia.month == self.periodo.mes:
            return Decimal(str(self.importe_recargo_mes))
        return Decimal(str(self.importe_recargo_mes_siguiente))

    def get_importe_total_con_mora(self, fecha_referencia) -> Decimal:
        return self.get_importe_total_base() + self.get_recargo_aplicable(fecha_referencia)

    def get_total_exigible(self, fecha_referencia) -> Decimal:
        return self.get_importe_total_con_mora(fecha_referencia)

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


class Donacion(models.Model):
    asociado = models.ForeignKey(Asociado, on_delete=models.CASCADE, related_name="donaciones")
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE, related_name="donaciones")
    importe = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Donación"
        verbose_name_plural = "Donaciones"
        ordering = ["-fecha", "-id"]

    def __str__(self):
        return f"Donación ${self.importe} - {self.asociado}"
