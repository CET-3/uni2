from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from django.db.models import Prefetch, Q
from django.utils import timezone

from asociados.models import Asociado
from config.formatting import formatear_moneda

from .models import Cuota, Pago, PeriodoCuota


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
class EstadoCredencial:
    activa: bool
    estado: str
    estado_display: str
    motivo: str | None


@dataclass(frozen=True)
class ResumenPago:
    pago: Pago
    lineas: list[str]


def calcular_estado_credencial(asociado: Asociado, fecha_referencia: date | None = None) -> EstadoCredencial:
    fecha_referencia = fecha_referencia or timezone.localdate()
    if asociado.estado != Asociado.ESTADO_ACTIVO:
        return EstadoCredencial(
            activa=False,
            estado="inactiva",
            estado_display="Inactiva",
            motivo="baja",
        )

    periodo_actual = (fecha_referencia.year, fecha_referencia.month)
    cuotas = getattr(asociado, "cuotas_para_estado_credencial", None)
    if cuotas is None:
        cuotas = asociado.cuotas.select_related("periodo", "periodo__ciclo_lectivo")
    for cuota in cuotas:
        periodo_cuota = (cuota.periodo.ciclo_lectivo.anio, cuota.periodo.mes)
        if periodo_cuota > periodo_actual:
            continue
        if periodo_cuota == periodo_actual and fecha_referencia.day <= 10:
            continue
        if cuota.get_saldo_pendiente(fecha_referencia) > 0:
            return EstadoCredencial(
                activa=False,
                estado="inactiva",
                estado_display="Inactiva",
                motivo="deuda",
            )

    return EstadoCredencial(
        activa=True,
        estado="activa",
        estado_display="Activa",
        motivo=None,
    )


def precargar_cuotas_para_estado_credencial(asociados):
    cuotas = Cuota.objects.select_related("periodo", "periodo__ciclo_lectivo")
    return asociados.prefetch_related(
        Prefetch(
            "cuotas",
            queryset=cuotas,
            to_attr="cuotas_para_estado_credencial",
        )
    )


def get_periodo_cuota_para_publicar(fecha_referencia=None):
    """Obtiene el período actual o el último anterior disponible.

    ``PeriodoCuota.activo`` controla la generación de cuotas, no la vigencia
    pública de su importe. Por eso esta consulta se guía por año y mes.
    """

    fecha_referencia = fecha_referencia or timezone.localdate()
    periodos = PeriodoCuota.objects.select_related("ciclo_lectivo")
    periodo_actual = periodos.filter(
        ciclo_lectivo__anio=fecha_referencia.year,
        mes=fecha_referencia.month,
    ).first()
    if periodo_actual:
        return periodo_actual

    periodo_anterior = (
        periodos.filter(
            Q(ciclo_lectivo__anio__lt=fecha_referencia.year)
            | Q(
                ciclo_lectivo__anio=fecha_referencia.year,
                mes__lt=fecha_referencia.month,
            )
        )
        .order_by("-ciclo_lectivo__anio", "-mes")
        .first()
    )
    if periodo_anterior:
        return periodo_anterior

    return periodos.order_by("-ciclo_lectivo__anio", "-mes").first()


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
        fecha_referencia = timezone.localdate()
    return sum(
        (cuota.get_saldo_pendiente(fecha_referencia) for cuota in get_cuotas_deudoras(asociado)),
        start=Decimal("0"),
    )
