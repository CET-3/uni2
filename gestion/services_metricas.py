"""Composición del tablero y variaciones; no contiene consultas por persona."""
from decimal import Decimal

from django.utils import timezone
from django.utils.formats import number_format

from config.formatting import formatear_moneda
from .selectors_metricas import (
    composicion_actual, metricas_cuotas, metricas_deuda, metricas_ingresos,
    metricas_padron, metricas_solicitudes, oferta_actual, porcentaje,
)


def variacion(actual, anterior, favorable="suba"):
    if actual is None or anterior is None:
        return None
    diferencia = Decimal(actual) - Decimal(anterior)
    positiva = diferencia > 0
    clase = "text-secondary" if not diferencia else "text-success" if positiva == (favorable == "suba") else "text-danger"
    return {"diferencia": diferencia, "porcentaje": porcentaje(diferencia, anterior) if anterior > 0 else None,
        "flecha": "↑" if positiva else "↓" if diferencia < 0 else "→", "clase": clase}


def construir_metricas(periodo, comparacion=None, tipo="todos", hoy=None):
    hoy = hoy or timezone.localdate()
    padron = metricas_padron(periodo, tipo)
    cuotas = metricas_cuotas(periodo, tipo, hoy)
    previo_padron = metricas_padron(comparacion, tipo) if comparacion else None
    previo_cuotas = metricas_cuotas(comparacion, tipo, hoy) if comparacion else None
    cards = []
    for titulo, valor, anterior, moneda, color, icono, ayuda in (
        ("Activos al cierre", padron["activos"], previo_padron["activos"] if comparacion else None, False, "blue", "people", "Según las fechas de alta y baja conservadas."),
        ("Cuotas generadas", cuotas["generado"], previo_cuotas["generado"] if comparacion else None, True, "green", "receipt", "Importe base real de las cuotas; sin recargos."),
        ("Cobrado de esas cuotas", cuotas["cobrado"], previo_cuotas["cobrado"] if comparacion else None, True, "yellow", "cash-coin", "Capital aplicado a esas cuotas hasta hoy, incluidos pagos posteriores."),
        ("Cumplimiento por monto", cuotas["cumplimiento"], previo_cuotas["cumplimiento"] if comparacion else None, False, "blue", "percent", "Cobrado de esas cuotas / generado. Sin cuotas, no se calcula."),
    ):
        cambio = variacion(valor, anterior) if comparacion else None
        es_porcentaje = icono == "percent"
        if cambio:
            cambio["texto"] = formatear_moneda(abs(cambio["diferencia"])) if moneda else number_format(abs(cambio["diferencia"]), decimal_pos=1 if es_porcentaje else 0) + (" pp" if es_porcentaje else "")
        texto = "No disponible" if valor is None else formatear_moneda(valor) if moneda else number_format(valor, decimal_pos=1 if es_porcentaje else 0) + (" %" if es_porcentaje else "")
        cards.append({"titulo": titulo, "valor": texto, "cambio": cambio, "color": color, "icono": icono, "ayuda": ayuda})
    return {"hoy": hoy, "padron": padron, "cuotas": cuotas, "cards": cards,
        "ingresos": metricas_ingresos(periodo, tipo), "deuda": metricas_deuda(tipo, hoy),
        "composicion": composicion_actual(), "solicitudes": metricas_solicitudes(periodo, tipo), "oferta": oferta_actual()}
