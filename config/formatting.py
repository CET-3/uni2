from decimal import Decimal, InvalidOperation

from django.utils import formats


def formatear_importe(valor) -> str:
    """Devuelve un importe con formato argentino y siempre dos decimales."""

    try:
        decimal = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        return str(valor)
    return formats.number_format(
        decimal,
        decimal_pos=2,
        use_l10n=True,
        force_grouping=True,
    )


def formatear_moneda(valor) -> str:
    return f"$ {formatear_importe(valor)}"
