"""Consultas del tablero diario: agregados SQL y detalle paginado.

No se unen simultáneamente aplicaciones y donaciones: ambas relaciones pueden
tener varias filas y multiplicar los importes. Cada suma usa su subconsulta.
"""

from decimal import Decimal
from datetime import datetime, time, timedelta

from django.db.models import CharField, Count, DecimalField, F, OuterRef, Q, Subquery, Sum, Value
from django.db.models.functions import Cast, Coalesce, Round, TruncDate
from django.utils import timezone

from asociados.models import Asociado, SolicitudAsociacion
from auditoria.models import EventoAuditoria
from cuotas.models import Donacion, Pago, PagoCuota

from .permissions import GESTION_VER_COBROS_EQUIPO


# Identificación heredada del importador; no inferirla por falta de auditoría.
PAGO_HISTORICO = Q(observaciones__startswith="Importado desde planilla historica de cuotas.")


def pagos_visibles(user, *, equipo=False):
    pagos = Pago.objects.all()
    if not (equipo and user.has_perm(GESTION_VER_COBROS_EQUIPO)):
        pagos = pagos.filter(registrado_por=user)
    return pagos


def pagos_del_periodo(user, periodo, *, equipo=False, historicos=False):
    pagos = pagos_visibles(user, equipo=equipo).filter(fecha__range=(periodo.desde, periodo.hasta))
    # La fecha de los importados es una referencia del período, no del cobro.
    return pagos.filter(PAGO_HISTORICO) if historicos else pagos.exclude(PAGO_HISTORICO)


def resumir_pagos_historicos(user, periodo, *, equipo=False):
    resumen = pagos_del_periodo(user, periodo, equipo=equipo, historicos=True).aggregate(
        cantidad=Count("pk"), total=Sum("importe", default=0),
    )
    resumen["total"] = Decimal(resumen["total"]).quantize(Decimal("0.01"))
    return resumen


def _suma_por_pago(modelo):
    importes = modelo.objects.filter(pago_id=OuterRef("pk")).order_by().values("pago_id").annotate(total=Sum("importe"))
    return Coalesce(Subquery(importes.values("total")), Value(Decimal("0")), output_field=DecimalField(max_digits=16, decimal_places=2))


def con_aplicaciones(pagos):
    return pagos.annotate(
        total_cuotas=_suma_por_pago(PagoCuota),
        total_donaciones=_suma_por_pago(Donacion),
    ).annotate(
        # SQLite usa representación binaria para SUM(NUMERIC): comparar a la
        # precisión monetaria evita considerar 0.10 + 0.20 distinto de 0.30.
        diferencia_aplicaciones=Round(F("importe") - F("total_cuotas") - F("total_donaciones"), precision=2),
    )


def resumir_pagos(pagos):
    resumen = con_aplicaciones(pagos).aggregate(
        cantidad=Count("pk"), total=Sum("importe", default=0),
        efectivo=Sum("importe", filter=Q(metodo=Pago.METODO_EFECTIVO), default=0),
        cantidad_efectivo=Count("pk", filter=Q(metodo=Pago.METODO_EFECTIVO)),
        billetera=Sum("importe", filter=Q(metodo=Pago.METODO_BILLETERA), default=0),
        cantidad_billetera=Count("pk", filter=Q(metodo=Pago.METODO_BILLETERA)),
        cuotas_recargos=Sum("total_cuotas", default=0),
        donaciones=Sum("total_donaciones", default=0),
        inconsistentes=Count("pk", filter=~Q(diferencia_aplicaciones=0)),
    )
    for campo in ("total", "efectivo", "billetera", "cuotas_recargos", "donaciones"):
        resumen[campo] = Decimal(resumen[campo]).quantize(Decimal("0.01"))
    resumen["diferencia"] = resumen["total"] - resumen["cuotas_recargos"] - resumen["donaciones"]
    return resumen


def con_fecha_carga(pagos):
    creacion = EventoAuditoria.objects.filter(
        entidad="cuotas.Pago", accion=EventoAuditoria.ACCION_CREAR,
        objeto_id=Cast(OuterRef("pk"), output_field=CharField()),
    ).order_by("fecha", "pk")
    return pagos.annotate(registrado_en=Subquery(creacion.values("fecha")[:1]))


def pagos_cargados_con_otra_fecha(user, periodo, *, equipo=False):
    inicio = timezone.make_aware(datetime.combine(periodo.desde, time.min))
    fin = timezone.make_aware(datetime.combine(periodo.hasta + timedelta(days=1), time.min))
    creaciones = EventoAuditoria.objects.filter(
        entidad="cuotas.Pago", accion=EventoAuditoria.ACCION_CREAR,
        fecha__gte=inicio, fecha__lt=fin,
    )
    # Primero acotar a ids con creaciones en el rango. Sólo después consultar
    # su primera creación, para no reconstruir la carga de todos los pagos.
    candidatos = pagos_visibles(user, equipo=equipo).exclude(PAGO_HISTORICO).alias(
        id_auditoria=Cast("pk", output_field=CharField()),
    ).filter(id_auditoria__in=Subquery(creaciones.values("objeto_id")))
    # TruncDate usa el timezone activo; un timestamp UTC no define el día local.
    return con_fecha_carga(candidatos).annotate(
        dia_carga=TruncDate("registrado_en"),
    ).filter(dia_carga__range=(periodo.desde, periodo.hasta)).exclude(fecha=F("dia_carga"))


def preparar_lista_pagos(pagos):
    return pagos.select_related("asociado", "registrado_por").order_by("-fecha", "-pk")


def altas_del_periodo(periodo):
    return Asociado.objects.filter(fecha_alta__range=(periodo.desde, periodo.hasta)).select_related(
        "curso_actual", "clasificacion_adherente",
    ).order_by("-fecha_alta", "apellido", "nombre", "pk")


def resumir_altas(periodo):
    return altas_del_periodo(periodo).aggregate(
        total=Count("pk"),
        asociados=Count("pk", filter=Q(tipo=Asociado.TIPO_ASOCIADO)),
        adherentes=Count("pk", filter=Q(tipo=Asociado.TIPO_ADHERENTE)),
    )


def solicitudes_pendientes():
    estados = (
        (SolicitudAsociacion.ESTADO_RECIBIDA, "Por revisar"),
        (SolicitudAsociacion.ESTADO_DATOS_APROBADOS, "Listas para el alta"),
        (SolicitudAsociacion.ESTADO_OBSERVADA, "Observadas"),
    )
    cantidades = SolicitudAsociacion.objects.aggregate(**{
        estado: Count("pk", filter=Q(estado=estado)) for estado, _ in estados
    })
    return [{"estado": estado, "label": label, "cantidad": cantidades[estado]} for estado, label in estados]
