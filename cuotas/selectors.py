from decimal import Decimal

from django.db.models import DecimalField, ExpressionWrapper, F, Sum

from asociados.models import Asociado

from .models import Cuota


def get_cuotas_deudoras(asociado: Asociado):
    return Cuota.objects.filter(asociado=asociado).exclude(
        estado__in=[Cuota.ESTADO_PAGADA, Cuota.ESTADO_BONIFICADA]
    ).select_related("periodo")


def get_total_deuda(asociado: Asociado):
    pendientes = get_cuotas_deudoras(asociado).annotate(
        deuda=ExpressionWrapper(F("importe") - F("importe_pagado"), output_field=DecimalField())
    )
    return pendientes.aggregate(total=Sum("deuda"))["total"] or Decimal("0")

