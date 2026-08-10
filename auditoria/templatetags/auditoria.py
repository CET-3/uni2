from django import template
from django.apps import apps

from config.formatting import formatear_moneda

from auditoria.presentacion import etiqueta_entidad


register = template.Library()

CAMPOS_LEGIBLES = {
    "nombre": "Nombre",
    "apellido": "Apellido",
    "dni": "DNI",
    "email": "Email",
    "telefono": "Teléfono",
    "direccion": "Dirección",
    "tipo": "Tipo",
    "curso_actual": "Curso actual",
    "estado": "Estado",
    "fecha_alta": "Fecha de alta",
    "fecha_inicio_cobro": "Fecha de inicio de cobro",
    "fecha_baja": "Fecha de baja",
    "motivo_baja": "Motivo de baja",
    "metodo": "Método",
}

CAMPOS_MONETARIOS = {
    "importe",
    "importe_pagado",
    "importe_recargo_mes",
    "importe_recargo_mes_siguiente",
    "precio_asociados",
    "precio_no_asociados",
}


@register.filter
def etiqueta_campo_auditoria(nombre, entidad=None):
    if nombre in CAMPOS_LEGIBLES:
        return CAMPOS_LEGIBLES[nombre]
    if entidad and "." in entidad:
        app_label, model_name = entidad.split(".", 1)
        model = apps.get_model(app_label, model_name)
        if model is not None:
            try:
                return str(model._meta.get_field(nombre).verbose_name).capitalize()
            except Exception:  # noqa: BLE001
                pass
    return str(nombre).replace("_", " ").capitalize()


@register.filter
def valor_auditoria(valor):
    if valor is None or valor == "":
        return "—"
    if isinstance(valor, dict) and "texto" in valor:
        return valor["texto"]
    if isinstance(valor, (list, tuple)):
        if not valor:
            return "—"
        return ", ".join(str(valor_auditoria(item)) for item in valor)
    if isinstance(valor, bool):
        return "Sí" if valor else "No"
    return valor


@register.filter
def actor_evento_auditoria(evento):
    if evento.actor_id:
        nombre_completo = evento.actor.get_full_name().strip()
        if nombre_completo:
            return nombre_completo
    return evento.actor_etiqueta


def _valor_nuevo(evento, campo):
    return evento.cambios.get(campo, {}).get("nuevo")


def _texto_relacion(valor):
    if isinstance(valor, dict):
        return valor.get("texto", "")
    return str(valor or "")


def _cuota_legible(texto):
    if " - " not in texto:
        return texto
    asociado, periodo = texto.rsplit(" - ", 1)
    return f"{periodo} de {asociado}"


@register.filter
def verbo_evento_auditoria(evento):
    verbos_especificos = {
        ("cuotas.Pago", "crear"): "registró",
        ("cuotas.PagoCuota", "crear"): "aplicó",
        ("cuotas.Donacion", "crear"): "registró",
        ("cuotas.Cuota", "modificar"): "actualizó",
    }
    if hasattr(evento, "accion"):
        verbo = verbos_especificos.get((evento.entidad, evento.accion))
        if verbo:
            return verbo
        accion = evento.accion
    else:
        accion = evento
    return {
        "crear": "creó",
        "modificar": "modificó",
        "cambiar_estado": "cambió el estado de",
        "vincular": "vinculó",
        "desvincular": "desvinculó",
        "anular": "anuló",
        "eliminar": "eliminó",
    }.get(accion, accion)


@register.filter
def objeto_evento_auditoria(evento):
    if evento.entidad == "cuotas.Pago" and evento.accion == "crear":
        importe = _valor_nuevo(evento, "importe")
        asociado = _texto_relacion(_valor_nuevo(evento, "asociado"))
        return f"un pago de {formatear_moneda(importe)} para {asociado}"
    if evento.entidad == "cuotas.PagoCuota" and evento.accion == "crear":
        importe = _valor_nuevo(evento, "importe")
        cuota = _cuota_legible(_texto_relacion(_valor_nuevo(evento, "cuota")))
        return f"{formatear_moneda(importe)} a la cuota {cuota}"
    if evento.entidad == "cuotas.Donacion" and evento.accion == "crear":
        importe = _valor_nuevo(evento, "importe")
        asociado = _texto_relacion(_valor_nuevo(evento, "asociado"))
        return f"una donación de {formatear_moneda(importe)} para {asociado}"
    if evento.entidad == "cuotas.Cuota" and evento.accion == "modificar":
        return f"la cuota {_cuota_legible(evento.objeto_descripcion)}"
    return evento.objeto_descripcion


@register.filter
def mostrar_campo_auditoria(campo, entidad):
    return not (entidad == "cuotas.Pago" and campo == "registrado_por")


@register.simple_tag
def valor_campo_auditoria(valor, campo, entidad):
    if valor is None or valor == "":
        return "—"
    if campo in CAMPOS_MONETARIOS:
        return formatear_moneda(valor)

    if entidad and "." in entidad:
        app_label, model_name = entidad.split(".", 1)
        model = apps.get_model(app_label, model_name)
        if model is not None:
            try:
                field = model._meta.get_field(campo)
                choices = dict(field.flatchoices)
                if valor in choices:
                    return choices[valor]
                if field.get_internal_type() in {"DateField", "DateTimeField"} and valor:
                    anio, mes, dia = str(valor)[:10].split("-")
                    return f"{dia}/{mes}/{anio}"
            except (KeyError, TypeError, ValueError):
                pass

    return valor_auditoria(valor)


@register.filter
def etiqueta_entidad_auditoria(entidad):
    return etiqueta_entidad(entidad)
