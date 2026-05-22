from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Asiento, CuentaContable, PartidaAsiento


def create_asiento(**kwargs):
    return Asiento.objects.create(**kwargs)


def validar_asiento(asiento: Asiento):
    try:
        asiento.validate_partidas_balanceadas()
    except ValidationError as exc:
        raise ValueError("; ".join(exc.messages)) from exc
    return asiento


def get_default_cuentas():
    cuentas = {
        cuenta.codigo: cuenta
        for cuenta in CuentaContable.objects.filter(codigo__in=["1.1.01", "1.1.02", "4.1.01"])
    }
    faltantes = {"1.1.01", "1.1.02", "4.1.01"} - set(cuentas)
    if faltantes:
        faltantes_str = ", ".join(sorted(faltantes))
        raise ValueError(
            "Faltan cuentas contables iniciales. Ejecuta el bootstrap de Uni2. "
            f"Codigos faltantes: {faltantes_str}"
        )
    return {
        "caja": cuentas["1.1.01"],
        "billetera_virtual": cuentas["1.1.02"],
        "ingresos_cuotas": cuentas["4.1.01"],
    }


@transaction.atomic
def registrar_asiento_pago_cuota(*, pago, descripcion: str):
    cuentas = get_default_cuentas()
    metodo_a_cuenta = {
        "efectivo": "caja",
        "billetera_virtual": "billetera_virtual",
    }
    cuenta_origen = cuentas[metodo_a_cuenta[pago.metodo]]
    cuenta_contrapartida = cuentas["ingresos_cuotas"]

    asiento = Asiento.objects.create(
        fecha=pago.fecha,
        descripcion=descripcion,
        tipo=Asiento.TIPO_INGRESO,
        importe=Decimal(str(pago.importe)),
        origen=pago,
    )
    PartidaAsiento.objects.bulk_create(
        [
            PartidaAsiento(
                asiento=asiento,
                cuenta=cuenta_origen,
                movimiento=PartidaAsiento.MOVIMIENTO_DEBE,
                importe=pago.importe,
                detalle="Ingreso del cobro",
            ),
            PartidaAsiento(
                asiento=asiento,
                cuenta=cuenta_contrapartida,
                movimiento=PartidaAsiento.MOVIMIENTO_HABER,
                importe=pago.importe,
                detalle="Reconocimiento de ingreso por cuotas",
            ),
        ]
    )
    return validar_asiento(asiento)
