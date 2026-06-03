from __future__ import annotations

from decimal import Decimal

from django.db import transaction

from asociados.models import Asociado
from contabilidad.services import registrar_asiento_pago_cuota

from .models import Cuota, Pago, PagoCuota, PeriodoCuota
from .selectors import get_cuotas_deudoras, get_total_deuda


def _periodo_key(periodo: PeriodoCuota) -> tuple[int, int]:
    return periodo.ciclo_lectivo.anio, periodo.mes


def _recompute_estado(cuota: Cuota):
    from django.utils import timezone

    fecha_referencia = timezone.localdate()
    total_exigible = cuota.get_total_exigible(fecha_referencia)
    if cuota.importe_pagado == 0:
        if cuota.paga_mora(fecha_referencia):
            cuota.estado = Cuota.ESTADO_VENCIDA
        else:
            cuota.estado = Cuota.ESTADO_PENDIENTE
    elif cuota.importe_pagado < total_exigible:
        cuota.estado = Cuota.ESTADO_PARCIAL
    elif cuota.importe_pagado >= total_exigible:
        cuota.estado = Cuota.ESTADO_PAGADA
    cuota.save(update_fields=["importe_pagado", "estado"])


@transaction.atomic
def generar_cuotas_para_periodo(periodo: PeriodoCuota) -> int:
    created = 0
    asociados = Asociado.objects.filter(
        estado=Asociado.ESTADO_ACTIVO,
        fecha_inicio_cobro__isnull=False,
    )
    for asociado in asociados:
        inicio = (asociado.fecha_inicio_cobro.year, asociado.fecha_inicio_cobro.month)
        if inicio > _periodo_key(periodo):
            continue
        _, was_created = Cuota.objects.get_or_create(
            asociado=asociado,
            periodo=periodo,
            defaults={
                "importe": periodo.importe,
                "importe_recargo_mora": periodo.importe_recargo_mora,
            },
        )
        created += int(was_created)
    return created


@transaction.atomic
def registrar_pago(*, asociado: Asociado, fecha, importe, metodo, registrado_por=None, observaciones=""):
    importe = Decimal(str(importe))
    deuda_total = get_total_deuda(asociado, fecha)
    if deuda_total <= 0:
        raise ValueError("El asociado no tiene deuda.")
    if importe > deuda_total:
        raise ValueError("El pago no puede superar la deuda.")

    pago = Pago.objects.create(
        asociado=asociado,
        fecha=fecha,
        importe=importe,
        metodo=metodo,
        registrado_por=registrado_por,
        observaciones=observaciones,
    )

    restante = importe
    cuotas = get_cuotas_deudoras(asociado).order_by("periodo__ciclo_lectivo__anio", "periodo__mes", "id")
    for cuota in cuotas:
        if restante <= 0:
            break
        saldo = cuota.get_saldo_pendiente(fecha)
        aplicado = min(restante, saldo)
        if aplicado <= 0:
            continue

        PagoCuota.objects.create(pago=pago, cuota=cuota, importe=aplicado)
        cuota.importe_pagado += aplicado
        _recompute_estado(cuota)
        restante -= aplicado

    registrar_asiento_pago_cuota(
        pago=pago,
        descripcion=f"Pago de cuotas asociado {asociado.numero_asociado}",
    )
    return pago
