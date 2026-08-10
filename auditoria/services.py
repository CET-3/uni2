from datetime import date, datetime
from decimal import Decimal

from django.db.models import Model
from django.db.models.fields.files import FieldFile

from .models import EventoAuditoria


def serializar_valor_auditable(valor):
    if isinstance(valor, (date, datetime)):
        return valor.isoformat()
    if isinstance(valor, Decimal):
        return str(valor)
    if isinstance(valor, FieldFile):
        return valor.name or ""
    if isinstance(valor, Model):
        return {"id": valor.pk, "texto": str(valor)}
    if isinstance(valor, dict):
        return {clave: serializar_valor_auditable(item) for clave, item in valor.items()}
    if isinstance(valor, (list, tuple, set)):
        return [serializar_valor_auditable(item) for item in valor]
    return valor


def construir_cambios(*, anteriores, nuevos, campos):
    cambios = {}
    for campo in campos:
        anterior = serializar_valor_auditable(anteriores.get(campo))
        nuevo = serializar_valor_auditable(nuevos.get(campo))
        if anterior != nuevo:
            cambios[campo] = {"anterior": anterior, "nuevo": nuevo}
    return cambios


def registrar_evento(
    *,
    actor,
    accion,
    entidad,
    objeto_id,
    objeto_descripcion,
    cambios,
    origen,
    motivo="",
    operacion_id=None,
    actor_etiqueta="",
):
    if actor is not None:
        actor_etiqueta = actor.get_full_name().strip() or actor.get_username()
    if not actor_etiqueta:
        raise ValueError("La auditoría requiere identificar a la persona o al proceso.")

    datos = {
        "actor": actor,
        "actor_etiqueta": actor_etiqueta,
        "accion": accion,
        "entidad": entidad,
        "objeto_id": str(objeto_id),
        "objeto_descripcion": objeto_descripcion,
        "cambios": cambios,
        "motivo": motivo,
        "origen": origen,
    }
    if operacion_id is not None:
        datos["operacion_id"] = operacion_id
    return EventoAuditoria.objects.create(**datos)
