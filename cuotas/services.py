from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from asociados.models import Asociado

from .models import Cuota, Donacion, Pago, PagoCuota, PeriodoCuota
from .selectors import calcular_estado_cuota, get_cuotas_deudoras


def _periodo_key(periodo: PeriodoCuota) -> tuple[int, int]:
    return periodo.ciclo_lectivo.anio, periodo.mes


def _recompute_estado(cuota: Cuota, fecha_referencia=None):
    if fecha_referencia is None:
        fecha_referencia = timezone.localdate()
    cuota.estado = calcular_estado_cuota(cuota, fecha_referencia).estado
    cuota.save(update_fields=["importe_pagado", "estado"])


def _get_cuotas_para_cobro(asociado: Asociado, cuotas_ids):
    cuotas_deudoras = list(
        get_cuotas_deudoras(asociado).order_by("periodo__ciclo_lectivo__anio", "periodo__mes", "id")
    )
    if cuotas_ids is None:
        return cuotas_deudoras
    cuotas_ids = [int(cuota_id) for cuota_id in cuotas_ids]
    if not cuotas_ids:
        raise ValueError("Debe seleccionar al menos una cuota para cobrar.")

    cuotas_por_id = {cuota.id: cuota for cuota in cuotas_deudoras}
    if any(cuota_id not in cuotas_por_id for cuota_id in cuotas_ids):
        raise ValueError("Las cuotas seleccionadas no corresponden a deuda vigente del asociado.")

    seleccionadas = [cuotas_por_id[cuota_id] for cuota_id in cuotas_ids]
    seleccionadas_ids = {cuota.id for cuota in seleccionadas}
    primeras_deudoras = cuotas_deudoras[: len(seleccionadas)]
    if {cuota.id for cuota in primeras_deudoras} != seleccionadas_ids:
        raise ValueError("El cobro debe incluir la deuda más antigua.")
    return primeras_deudoras


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


def generar_cuotas_iniciales_para_asociado(*, asociado: Asociado, fecha_referencia) -> list[Cuota]:
    meses = []
    for i in range(2, -1, -1):
        m = fecha_referencia.month - i
        a = fecha_referencia.year
        while m < 1:
            m += 12
            a -= 1
        meses.append((a, m))

    cuotas = []
    for anio, mes in meses:
        try:
            periodo = PeriodoCuota.objects.get(mes=mes, ciclo_lectivo__anio=anio, activo=True)
        except PeriodoCuota.DoesNotExist:
            continue
        cuota, _ = Cuota.objects.get_or_create(
            asociado=asociado,
            periodo=periodo,
            defaults={
                "importe": periodo.importe,
                "importe_recargo_mes": periodo.importe_recargo_mes,
                "importe_recargo_mes_siguiente": periodo.importe_recargo_mes_siguiente,
            },
        )
        cuotas.append(cuota)
    return cuotas


@transaction.atomic
def registrar_pago(*, asociado: Asociado, fecha, importe, metodo, registrado_por=None, observaciones="", cuotas_ids=None):
    importe = Decimal(str(importe))
    cuotas = _get_cuotas_para_cobro(asociado, cuotas_ids)
    deuda_total = sum((cuota.get_saldo_pendiente(fecha) for cuota in cuotas), start=Decimal("0"))
    if deuda_total <= 0:
        raise ValueError("El asociado no tiene deuda.")
    if importe < deuda_total:
        raise ValueError("El pago no puede ser menor a la deuda total.")

    importe_recibido = importe
    importe_cuotas = deuda_total
    importe_donacion = importe_recibido - importe_cuotas

    pago = Pago.objects.create(
        asociado=asociado,
        fecha=fecha,
        importe=importe_recibido,
        metodo=metodo,
        registrado_por=registrado_por,
        observaciones=observaciones,
    )

    restante = importe_cuotas
    for cuota in cuotas:
        if restante <= 0:
            break
        saldo = cuota.get_saldo_pendiente(fecha)
        aplicado = min(restante, saldo)
        if aplicado <= 0:
            continue

        PagoCuota.objects.create(pago=pago, cuota=cuota, importe=aplicado)
        cuota.importe_pagado += aplicado
        _recompute_estado(cuota, fecha)
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


