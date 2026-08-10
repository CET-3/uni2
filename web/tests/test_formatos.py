from decimal import Decimal

from config.formatting import formatear_moneda


def test_formatear_moneda_usa_separadores_argentinos_y_dos_decimales():
    assert formatear_moneda(Decimal("1234567.5")) == "$ 1.234.567,50"
    assert formatear_moneda(Decimal("0")) == "$ 0,00"
