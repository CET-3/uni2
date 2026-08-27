from __future__ import annotations

import uuid
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from asociados.models import Asociado
from auditoria.models import EventoAuditoria
from auditoria.services import construir_cambios, registrar_evento

from .models import Cuota, Donacion, Pago, PagoCuota, PeriodoCuota
from .selectors import calcular_estado_cuota, get_cuotas_deudoras


AUDIT_FIELDS_PERIODO = (
    "mes",
    "ciclo_lectivo",
    "importe",
    "importe_recargo_mes",
    "importe_recargo_mes_siguiente",
    "fecha_vencimiento",
    "activo",
    "generado_el",
)
AUDIT_FIELDS_CUOTA = (
    "asociado",
    "periodo",
    "importe",
    "importe_recargo_mes",
    "importe_recargo_mes_siguiente",
    "importe_pagado",
    "estado",
)
AUDIT_FIELDS_PAGO = ("asociado", "fecha", "importe", "metodo", "observaciones")
AUDIT_FIELDS_PAGO_CUOTA = ("pago", "cuota", "importe")
AUDIT_FIELDS_DONACION = ("asociado", "pago", "importe", "fecha", "observaciones")


def _snapshot(obj, fields):
    return {field: getattr(obj, field) for field in fields}


def _registrar_creacion(*, obj, fields, actor, origen, operacion_id, actor_etiqueta):
    nuevos = _snapshot(obj, fields)
    registrar_evento(
        actor=actor,
        actor_etiqueta=actor_etiqueta,
        accion=EventoAuditoria.ACCION_CREAR,
        entidad=obj._meta.label,
        objeto_id=obj.pk,
        objeto_descripcion=str(obj),
        cambios=construir_cambios(
            anteriores={field: None for field in fields},
            nuevos=nuevos,
            campos=fields,
        ),
        origen=origen,
        operacion_id=operacion_id,
    )


def _periodo_key(periodo: PeriodoCuota) -> tuple[int, int]:
    return periodo.ciclo_lectivo.anio, periodo.mes


def _get_periodos_activos_para_alta():
    return (
        PeriodoCuota.objects.select_for_update()
        .filter(activo=True)
        .select_related("ciclo_lectivo")
        .order_by("ciclo_lectivo__anio", "mes")
    )


def _recompute_estado(cuota: Cuota, fecha_referencia=None):
    if fecha_referencia is None:
        fecha_referencia = timezone.localdate()
    cuota.estado = calcular_estado_cuota(cuota, fecha_referencia).estado
    cuota.save(update_fields=["importe_pagado", "estado"])


def _get_cuotas_para_cobro(asociado: Asociado, cuotas_ids, fecha_referencia):
    cuotas_deudoras = list(
        get_cuotas_deudoras(asociado, fecha_referencia).order_by(
            "periodo__ciclo_lectivo__anio", "periodo__mes", "id"
        )
    )
    if cuotas_ids is None:
        return cuotas_deudoras
    cuotas_ids = [int(cuota_id) for cuota_id in cuotas_ids]
    if not cuotas_ids:
        if not cuotas_deudoras:
            return []
        raise ValueError("Debe seleccionar al menos una cuota para cobrar.")

    cuotas_por_id = {cuota.id: cuota for cuota in cuotas_deudoras}
    if any(cuota_id not in cuotas_por_id for cuota_id in cuotas_ids):
        raise ValueError("Las cuotas seleccionadas no corresponden a deuda vigente del asociado.")

    seleccionadas = [cuotas_por_id[cuota_id] for cuota_id in cuotas_ids]
    seleccionadas_ids = {cuota.id for cuota in seleccionadas}
    primeras_deudoras = cuotas_deudoras[: len(seleccionadas)]
    if {cuota.id for cuota in primeras_deudoras} != seleccionadas_ids:
        raise ValueError("El cobro debe incluir la deuda más antigua.")
    return primeras_deudoras


@transaction.atomic
def crear_periodo_cuota(*, datos, actor):
    periodo = PeriodoCuota(**datos)
    periodo.full_clean()
    periodo.save()
    _registrar_creacion(
        obj=periodo,
        fields=AUDIT_FIELDS_PERIODO,
        actor=actor,
        origen=EventoAuditoria.ORIGEN_GESTION,
        operacion_id=uuid.uuid4(),
        actor_etiqueta="Sistema: creación de período",
    )
    return periodo


@transaction.atomic
def generar_cuotas_para_periodo(periodo: PeriodoCuota, *, actor=None) -> int:
    created = 0
    operacion_id = uuid.uuid4()
    periodo = PeriodoCuota.objects.select_for_update().get(pk=periodo.pk)
    asociados = Asociado.objects.filter(
        estado=Asociado.ESTADO_ACTIVO,
        fecha_inicio_cobro__isnull=False,
    )
    for asociado in asociados:
        inicio = (asociado.fecha_inicio_cobro.year, asociado.fecha_inicio_cobro.month)
        if inicio > _periodo_key(periodo):
            continue
        cuota, was_created = Cuota.objects.get_or_create(
            asociado=asociado,
            periodo=periodo,
            defaults={
                "importe": periodo.importe,
                "importe_recargo_mes": periodo.importe_recargo_mes,
                "importe_recargo_mes_siguiente": periodo.importe_recargo_mes_siguiente,
            },
        )
        created += int(was_created)
        if was_created:
            _registrar_creacion(
                obj=cuota,
                fields=AUDIT_FIELDS_CUOTA,
                actor=actor,
                origen=EventoAuditoria.ORIGEN_GESTION if actor else EventoAuditoria.ORIGEN_SISTEMA,
                operacion_id=operacion_id,
                actor_etiqueta="Sistema: generación de cuotas",
            )
    if periodo.generado_el is None:
        anteriores = {"generado_el": None}
        periodo.generado_el = timezone.now()
        periodo.save(update_fields=["generado_el"])
        registrar_evento(
            actor=actor,
            actor_etiqueta="Sistema: generación de cuotas",
            accion=EventoAuditoria.ACCION_MODIFICAR,
            entidad=periodo._meta.label,
            objeto_id=periodo.pk,
            objeto_descripcion=str(periodo),
            cambios=construir_cambios(
                anteriores=anteriores,
                nuevos={"generado_el": periodo.generado_el},
                campos=("generado_el",),
            ),
            origen=EventoAuditoria.ORIGEN_GESTION if actor else EventoAuditoria.ORIGEN_SISTEMA,
            operacion_id=operacion_id,
        )
    return created


@transaction.atomic
def generar_cuotas_iniciales_para_asociado(
    *,
    asociado: Asociado,
    fecha_referencia,
    actor=None,
    operacion_id=None,
) -> list[Cuota]:
    if asociado.fecha_inicio_cobro is None:
        return []

    cuotas = []
    operacion_id = operacion_id or uuid.uuid4()
    inicio = (asociado.fecha_inicio_cobro.year, asociado.fecha_inicio_cobro.month)
    periodo_actual = (fecha_referencia.year, fecha_referencia.month)
    for periodo in _get_periodos_activos_para_alta():
        clave = _periodo_key(periodo)
        if clave < inicio:
            continue
        if clave > periodo_actual and periodo.generado_el is None:
            continue
        cuota, created = Cuota.objects.get_or_create(
            asociado=asociado,
            periodo=periodo,
            defaults={
                "importe": periodo.importe,
                "importe_recargo_mes": periodo.importe_recargo_mes,
                "importe_recargo_mes_siguiente": periodo.importe_recargo_mes_siguiente,
            },
        )
        if created:
            cuotas.append(cuota)
            _registrar_creacion(
                obj=cuota,
                fields=AUDIT_FIELDS_CUOTA,
                actor=actor,
                origen=EventoAuditoria.ORIGEN_GESTION if actor else EventoAuditoria.ORIGEN_SISTEMA,
                operacion_id=operacion_id,
                actor_etiqueta="Sistema: generación de cuotas iniciales",
            )
    return cuotas


@transaction.atomic
def registrar_pago(*, asociado: Asociado, fecha, importe, metodo, registrado_por=None, observaciones="", cuotas_ids=None):
    operacion_id = uuid.uuid4()
    origen = EventoAuditoria.ORIGEN_GESTION if registrado_por else EventoAuditoria.ORIGEN_SISTEMA
    actor_etiqueta = "Sistema: registro de pago"
    importe = Decimal(str(importe))
    cuotas = _get_cuotas_para_cobro(asociado, cuotas_ids, fecha)
    deuda_total = sum((cuota.get_saldo_pendiente(fecha) for cuota in cuotas), start=Decimal("0"))
    es_donacion_sin_deuda = not cuotas and cuotas_ids == []
    if deuda_total <= 0 and not es_donacion_sin_deuda:
        raise ValueError("El asociado no tiene deuda.")
    if importe < deuda_total:
        raise ValueError("El pago no puede ser menor a la deuda total.")

    importe_recibido = importe
    importe_cuotas = deuda_total
    importe_donacion = importe_recibido - importe_cuotas

    pago = Pago.objects.create(
        asociado=asociado,
        fecha=fecha,
        importe=importe_recibido,
        metodo=metodo,
        registrado_por=registrado_por,
        observaciones=observaciones,
    )
    _registrar_creacion(
        obj=pago,
        fields=AUDIT_FIELDS_PAGO,
        actor=registrado_por,
        origen=origen,
        operacion_id=operacion_id,
        actor_etiqueta=actor_etiqueta,
    )

    restante = importe_cuotas
    for cuota in cuotas:
        if restante <= 0:
            break
        saldo = cuota.get_saldo_pendiente(fecha)
        aplicado = min(restante, saldo)
        if aplicado <= 0:
            continue

        aplicacion = PagoCuota.objects.create(pago=pago, cuota=cuota, importe=aplicado)
        _registrar_creacion(
            obj=aplicacion,
            fields=AUDIT_FIELDS_PAGO_CUOTA,
            actor=registrado_por,
            origen=origen,
            operacion_id=operacion_id,
            actor_etiqueta=actor_etiqueta,
        )
        cuota_anterior = _snapshot(cuota, ("importe_pagado", "estado"))
        cuota.importe_pagado += aplicado
        _recompute_estado(cuota, fecha)
        cuota_nueva = _snapshot(cuota, ("importe_pagado", "estado"))
        registrar_evento(
            actor=registrado_por,
            actor_etiqueta=actor_etiqueta,
            accion=EventoAuditoria.ACCION_MODIFICAR,
            entidad=cuota._meta.label,
            objeto_id=cuota.pk,
            objeto_descripcion=str(cuota),
            cambios=construir_cambios(
                anteriores=cuota_anterior,
                nuevos=cuota_nueva,
                campos=("importe_pagado", "estado"),
            ),
            origen=origen,
            operacion_id=operacion_id,
        )
        restante -= aplicado

    if importe_donacion > 0:
        donacion = Donacion.objects.create(
            asociado=asociado,
            pago=pago,
            importe=importe_donacion,
            fecha=fecha,
            observaciones=observaciones,
        )
        _registrar_creacion(
            obj=donacion,
            fields=AUDIT_FIELDS_DONACION,
            actor=registrado_por,
            origen=origen,
            operacion_id=operacion_id,
            actor_etiqueta=actor_etiqueta,
        )

    return pago


@transaction.atomic
def registrar_donacion(
    *,
    asociado: Asociado,
    fecha,
    importe,
    metodo,
    registrado_por=None,
    observaciones="",
):
    """Registra una donación cuando el asociado no tiene cuotas pendientes."""

    if get_cuotas_deudoras(asociado, fecha).exists():
        raise ValueError("El asociado tiene cuotas pendientes; primero debe registrar su cobro.")
    return registrar_pago(
        asociado=asociado,
        fecha=fecha,
        importe=importe,
        metodo=metodo,
        registrado_por=registrado_por,
        observaciones=observaciones,
        cuotas_ids=[],
    )
