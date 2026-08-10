from decimal import Decimal
from dataclasses import dataclass
from datetime import date

from asociados.models import Asociado
from config.formatting import formatear_moneda

from .models import Cuota, Pago


@dataclass(frozen=True)
class EstadoCuota:
    cuota: Cuota
    fecha: date
    importe_original: Decimal
    recargo: Decimal
    total_exigible: Decimal
    importe_pagado: Decimal
    saldo: Decimal
    estado: str
    estado_display: str


@dataclass(frozen=True)
class ResumenPago:
    pago: Pago
    lineas: list[str]


def calcular_estado_cuota(cuota: Cuota, fecha_referencia) -> EstadoCuota:
    recargo = cuota.get_recargo_aplicable(fecha_referencia)
    total_exigible = cuota.get_total_exigible(fecha_referencia)
    importe_pagado = Decimal(str(cuota.importe_pagado))
    saldo = cuota.get_saldo_pendiente(fecha_referencia)
    if saldo <= 0:
        estado = Cuota.ESTADO_PAGADA
        estado_display = "Pagada"
    elif fecha_referencia > cuota.periodo.fecha_vencimiento:
        estado = Cuota.ESTADO_VENCIDA
        estado_display = "Vencida"
    else:
        estado = Cuota.ESTADO_PENDIENTE
        estado_display = "Pendiente"
    return EstadoCuota(
        cuota=cuota,
        fecha=fecha_referencia,
        importe_original=Decimal(str(cuota.importe)),
        recargo=recargo,
        total_exigible=total_exigible,
        importe_pagado=importe_pagado,
        saldo=saldo,
        estado=estado,
        estado_display=estado_display,
    )


def describir_pago(pago: Pago) -> ResumenPago:
    lineas = []
    aplicaciones = pago.aplicaciones.select_related("cuota__periodo", "cuota__periodo__ciclo_lectivo").order_by(
        "cuota__periodo__ciclo_lectivo__anio",
        "cuota__periodo__mes",
        "cuota_id",
    )
    periodos = [str(aplicacion.cuota.periodo) for aplicacion in aplicaciones]
    if periodos:
        lineas.append(f"Cuotas: {', '.join(periodos)}")

    for donacion in pago.donaciones.order_by("id"):
        lineas.append(f"Donación: {formatear_moneda(donacion.importe)}")

    if not lineas:
        lineas.append("Sin aplicaciones registradas")
    return ResumenPago(pago=pago, lineas=lineas)


def get_cuotas_deudoras(asociado: Asociado):
    return Cuota.objects.filter(asociado=asociado).exclude(estado=Cuota.ESTADO_PAGADA).select_related(
        "periodo", "periodo__ciclo_lectivo"
    )


def get_cuotas_deudoras_del_anio(asociado: Asociado, anio: int):
    return get_cuotas_deudoras(asociado).filter(periodo__ciclo_lectivo__anio=anio)


def get_cuotas_del_asociado(asociado: Asociado):
    return asociado.cuotas.select_related("periodo", "periodo__ciclo_lectivo")


def get_cuotas_del_anio(asociado: Asociado, anio: int):
    return get_cuotas_del_asociado(asociado).filter(periodo__ciclo_lectivo__anio=anio)


def get_total_deuda(asociado: Asociado, fecha_referencia=None):
    if fecha_referencia is None:
        from django.utils import timezone

        fecha_referencia = timezone.localdate()
    return sum(
        (cuota.get_saldo_pendiente(fecha_referencia) for cuota in get_cuotas_deudoras(asociado)),
        start=Decimal("0"),
    )
