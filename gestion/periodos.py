"""Intervalos de fechas locales compartidos por las consultas de gestión."""

from dataclasses import dataclass
from calendar import monthrange
from datetime import date, timedelta

from django.utils import timezone


@dataclass(frozen=True)
class Periodo:
    desde: date
    hasta: date


def resolver_periodo_atencion(nombre, desde=None, hasta=None, *, hoy=None):
    hoy = hoy or timezone.localdate()
    if nombre == "hoy":
        return Periodo(hoy, hoy)
    if nombre == "ayer":
        ayer = hoy - timedelta(days=1)
        return Periodo(ayer, ayer)
    if nombre == "esta_semana":
        return Periodo(hoy - timedelta(days=hoy.weekday()), hoy)
    if nombre != "personalizado":
        raise ValueError("Elegí un período válido.")
    if desde is None or hasta is None:
        raise ValueError("Indicá las dos fechas del período personalizado.")
    if desde > hasta:
        raise ValueError("La fecha desde no puede ser posterior a la fecha hasta.")
    if hasta > hoy:
        raise ValueError("El período no puede incluir fechas futuras.")
    return Periodo(desde, hasta)


def desplazar_meses(fecha, meses):
    ordinal = fecha.year * 12 + fecha.month - 1 + meses
    anio, mes = divmod(ordinal, 12)
    mes += 1
    return date(anio, mes, min(fecha.day, monthrange(anio, mes)[1]))


def resolver_periodo_metricas(nombre, desde=None, hasta=None, *, hoy=None):
    hoy = hoy or timezone.localdate()
    inicio_mes = hoy.replace(day=1)
    if nombre == "este_mes":
        return Periodo(inicio_mes, hoy)
    if nombre == "mes_anterior":
        return Periodo(desplazar_meses(inicio_mes, -1), inicio_mes - timedelta(days=1))
    if nombre == "este_anio":
        return Periodo(hoy.replace(month=1, day=1), hoy)
    if nombre == "ultimos_12_meses":
        return Periodo(desplazar_meses(inicio_mes, -11), hoy)
    return resolver_periodo_atencion(nombre, desde, hasta, hoy=hoy)


def comparar_periodo(periodo, nombre, preset):
    if nombre == "sin":
        return None
    if nombre == "anio_anterior":
        meses = -12
    elif nombre != "anterior":
        raise ValueError("Elegí una comparación válida.")
    elif preset in ("este_anio", "ultimos_12_meses"):
        meses = -12
    elif preset in ("este_mes", "mes_anterior"):
        meses = -1
    else:
        dias = 7 if preset == "esta_semana" else (periodo.hasta - periodo.desde).days + 1
        return Periodo(periodo.desde - timedelta(days=dias), periodo.hasta - timedelta(days=dias))
    desde = desplazar_meses(periodo.desde, meses)
    hasta = desplazar_meses(periodo.hasta, meses)
    if preset == "mes_anterior":
        hasta = desde.replace(day=monthrange(desde.year, desde.month)[1])
    return Periodo(desde, hasta)


def segmentos_periodo(periodo):
    cursor = periodo.desde
    diario = (periodo.hasta - periodo.desde).days < 31
    while cursor <= periodo.hasta:
        cierre = cursor if diario else cursor.replace(day=monthrange(cursor.year, cursor.month)[1])
        cierre = min(cierre, periodo.hasta)
        yield Periodo(cursor, cierre)
        cursor = cierre + timedelta(days=1)
