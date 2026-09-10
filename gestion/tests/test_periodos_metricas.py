from datetime import date

import pytest

from gestion.periodos import Periodo


@pytest.mark.parametrize("nombre,desde,hasta", [
    ("hoy", date(2026, 9, 10), date(2026, 9, 10)),
    ("esta_semana", date(2026, 9, 7), date(2026, 9, 10)),
    ("este_mes", date(2026, 9, 1), date(2026, 9, 10)),
    ("mes_anterior", date(2026, 8, 1), date(2026, 8, 31)),
    ("este_anio", date(2026, 1, 1), date(2026, 9, 10)),
    ("ultimos_12_meses", date(2025, 10, 1), date(2026, 9, 10)),
])
def test_periodos(nombre, desde, hasta):
    from gestion.periodos import resolver_periodo_metricas
    assert resolver_periodo_metricas(nombre, hoy=date(2026, 9, 10)) == Periodo(desde, hasta)


def test_comparaciones_alinean_periodos_parciales_y_bisiestos():
    from gestion.periodos import comparar_periodo
    actual = Periodo(date(2026, 9, 1), date(2026, 9, 10))
    assert comparar_periodo(actual, "anterior", "este_mes") == Periodo(date(2026, 8, 1), date(2026, 8, 10))
    assert comparar_periodo(actual, "anio_anterior", "este_mes") == Periodo(date(2025, 9, 1), date(2025, 9, 10))
    assert comparar_periodo(actual, "sin", "este_mes") is None
    assert comparar_periodo(Periodo(date(2024, 2, 29), date(2024, 2, 29)), "anio_anterior", "hoy") == Periodo(date(2023, 2, 28), date(2023, 2, 28))
    assert comparar_periodo(Periodo(date(2025, 2, 1), date(2025, 2, 28)), "anio_anterior", "mes_anterior") == Periodo(date(2024, 2, 1), date(2024, 2, 29))


def test_segmentos_no_salen_del_rango():
    from gestion.periodos import segmentos_periodo
    diario = list(segmentos_periodo(Periodo(date(2026, 9, 9), date(2026, 9, 10))))
    assert diario == [Periodo(date(2026, 9, 9), date(2026, 9, 9)), Periodo(date(2026, 9, 10), date(2026, 9, 10))]
    mensual = list(segmentos_periodo(Periodo(date(2026, 7, 20), date(2026, 9, 10))))
    assert mensual[0].desde == date(2026, 7, 20)
    assert mensual[-1].hasta == date(2026, 9, 10)
    assert len(mensual) == 3
