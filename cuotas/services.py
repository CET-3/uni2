from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from asociados.models import Asociado, CicloLectivo

from .models import Cuota, Donacion, Pago, PagoCuota, PeriodoCuota
from .selectors import get_cuotas_deudoras, get_total_deuda


def _periodo_key(periodo: PeriodoCuota) -> tuple[int, int]:
    return periodo.ciclo_lectivo.anio, periodo.mes


def _recompute_estado(cuota: Cuota):
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
                "importe_recargo_mes": periodo.importe_recargo_mes,
                "importe_recargo_mes_siguiente": periodo.importe_recargo_mes_siguiente,
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
    if importe < deuda_total:
        raise ValueError("El pago no puede ser menor a la deuda total.")

    importe_pago = deuda_total
    importe_donacion = importe - deuda_total

    pago = Pago.objects.create(
        asociado=asociado,
        fecha=fecha,
        importe=importe_pago,
        metodo=metodo,
        registrado_por=registrado_por,
        observaciones=observaciones,
    )

    restante = importe_pago
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

    if importe_donacion > 0:
        Donacion.objects.create(
            asociado=asociado,
            pago=pago,
            importe=importe_donacion,
            fecha=fecha,
            observaciones=observaciones,
        )

    return pago


@transaction.atomic
def generar_cuotas_y_pago_inicial(*, asociado: Asociado, fecha, importe, metodo, registrado_por=None, observaciones=""):
    """
    Genera cuotas retroactivas (2 meses) + mes corriente para un nuevo asociado
    y registra el pago correspondiente.
    """
    hoy = timezone.localdate()
    ciclo, _ = CicloLectivo.objects.get_or_create(anio=hoy.year)

    meses = []
    for i in range(2, -1, -1):
        m = hoy.month - i
        a = hoy.year
        while m < 1:
            m += 12
            a -= 1
        meses.append((a, m))

    cuotas_generadas = []
    for anio, mes in meses:
        ciclo_periodo, _ = CicloLectivo.objects.get_or_create(anio=anio)
        periodo, _ = PeriodoCuota.objects.get_or_create(
            mes=mes,
            ciclo_lectivo=ciclo_periodo,
            defaults={
                "importe": Decimal("800.00"),
                "importe_recargo_mes": Decimal("100.00"),
                "importe_recargo_mes_siguiente": Decimal("200.00"),
                "fecha_vencimiento": date(anio, mes, 10),
            },
        )
        cuota, created = Cuota.objects.get_or_create(
            asociado=asociado,
            periodo=periodo,
            defaults={
                "importe": periodo.importe,
                "importe_recargo_mes": periodo.importe_recargo_mes,
                "importe_recargo_mes_siguiente": periodo.importe_recargo_mes_siguiente,
            },
        )
        if created:
            cuotas_generadas.append(cuota)

    pago = registrar_pago(
        asociado=asociado,
        fecha=fecha,
        importe=importe,
        metodo=metodo,
        registrado_por=registrado_por,
        observaciones=observaciones,
    )
    return pago, cuotas_generadas
