from decimal import Decimal

from asociados.models import Asociado

from .models import Cuota


def get_cuotas_deudoras(asociado: Asociado):
    return Cuota.objects.filter(asociado=asociado).exclude(
        estado__in=[Cuota.ESTADO_PAGADA, Cuota.ESTADO_BONIFICADA]
    ).select_related("periodo", "periodo__ciclo_lectivo")


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
