"""Intervalos de fechas locales compartidos por las consultas de gestión."""

from dataclasses import dataclass
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
