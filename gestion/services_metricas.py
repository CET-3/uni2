"""Composición del tablero y variaciones; no contiene consultas por persona."""
from decimal import Decimal

from django.utils import timezone
from django.utils.formats import number_format

from config.formatting import formatear_moneda
from .selectors_metricas import (
    composicion_actual, metricas_credenciales, metricas_cuotas, metricas_deuda, metricas_ingresos,
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


def metrica_proporcion(titulo, valor, relacion, referencia, color, anterior=None):
    cambio = variacion(valor, anterior)
    if cambio:
        cambio["texto"] = number_format(abs(cambio["diferencia"]), decimal_pos=1) + " pp"
    return {"titulo": titulo, "valor": number_format(valor, decimal_pos=1) + " %" if valor is not None else "—",
        "progreso": max(0, min(100, valor)) if valor is not None else None,
        "relacion": relacion, "referencia": referencia, "color": color, "cambio": cambio}


def construir_metricas(periodo, comparacion=None, tipo="todos", hoy=None):
    hoy = hoy or timezone.localdate()
    padron = metricas_padron(periodo, tipo)
    cuotas = metricas_cuotas(periodo, tipo, hoy)
    credenciales = metricas_credenciales(tipo, hoy)
    previo_padron = metricas_padron(comparacion, tipo) if comparacion else None
    previo_cuotas = metricas_cuotas(comparacion, tipo, hoy) if comparacion else None
    cards = []
    for titulo, valor, anterior, moneda, color, icono, ayuda in (
        ("Padrón activo", padron["activos"], previo_padron["activos"] if comparacion else None, False, "blue", "people", "Al cierre del período, según altas y bajas conservadas."),
        ("Credenciales activas", credenciales["activas"], None, False, "green", "person-vcard", "Vigentes hoy para utilizar los beneficios de la mutual."),
        ("Cuotas generadas", cuotas["generado"], previo_cuotas["generado"] if comparacion else None, True, "yellow", "receipt", "Importe base real de las cuotas; sin recargos."),
        ("Cobrado de esas cuotas", cuotas["cobrado"], previo_cuotas["cobrado"] if comparacion else None, True, "red", "cash-coin", "Capital aplicado a esas cuotas hasta hoy, incluidos pagos posteriores."),
    ):
        cambio = variacion(valor, anterior) if comparacion else None
        if cambio:
            cambio["texto"] = formatear_moneda(abs(cambio["diferencia"])) if moneda else number_format(abs(cambio["diferencia"]), decimal_pos=0)
        texto = "No disponible" if valor is None else formatear_moneda(valor) if moneda else number_format(valor, decimal_pos=0)
        cards.append({"titulo": titulo, "valor": texto, "cambio": cambio, "color": color, "icono": icono, "ayuda": ayuda})
    proporciones = [
        metrica_proporcion("Credenciales activas", credenciales["porcentaje"],
            f'{credenciales["activas"]} de {credenciales["total"]} personas de alta' if credenciales["total"] else "Sin personas de alta en el padrón seleccionado",
            "Hoy · padrón seleccionado", "green"),
        metrica_proporcion("Cumplimiento por monto", cuotas["cumplimiento"],
            f'{formatear_moneda(cuotas["cobrado"])} cobrados de {formatear_moneda(cuotas["generado"])} generados' if cuotas["generado"] else "Sin cuotas generadas en el período",
            "Cuotas del período · cobrado hasta hoy", "blue", anterior=previo_cuotas["cumplimiento"] if comparacion else None),
    ]
    return {"hoy": hoy, "padron": padron, "cuotas": cuotas, "cards": cards, "credenciales": credenciales, "proporciones": proporciones,
        "ingresos": metricas_ingresos(periodo, tipo), "deuda": metricas_deuda(tipo, hoy),
        "composicion": composicion_actual(), "solicitudes": metricas_solicitudes(periodo, tipo), "oferta": oferta_actual()}
