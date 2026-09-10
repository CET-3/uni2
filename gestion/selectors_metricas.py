"""Consultas de Métricas. Las series recorren agregados, nunca todo el padrón."""

from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, DecimalField, Exists, F, OuterRef, Q, Subquery, Sum, Value
from django.db.models.functions import Coalesce, Greatest, Least, Round, TruncDay, TruncMonth
from django.utils import timezone

from asociados.models import Asociado, SolicitudAsociacion
from comercios.models import Comercio
from cuotas.models import Cuota, Pago, PagoCuota
from cuotas.selectors import cuotas_con_saldo, cuotas_que_inactivan_credencial
from .periodos import segmentos_periodo
from .selectors_atencion import PAGO_HISTORICO, resumir_pagos


def porcentaje(parte, total):
    return (Decimal(parte) * 100 / Decimal(total)).quantize(Decimal("0.1")) if total else None


def personas_metricas(tipo="todos"):
    personas = Asociado.objects.all()
    return personas if tipo == "todos" else personas.filter(tipo=tipo)


def activos_al_cierre(personas, fecha):
    return personas.filter(fecha_alta__lte=fecha).filter(Q(fecha_baja__isnull=True) | Q(fecha_baja__gt=fecha))


def metricas_padron(periodo, tipo="todos"):
    personas = personas_metricas(tipo)
    datos = personas.aggregate(
        altas=Count("pk", filter=Q(fecha_alta__range=(periodo.desde, periodo.hasta))),
        bajas=Count("pk", filter=Q(fecha_baja__range=(periodo.desde, periodo.hasta))),
        inconsistentes=Count("pk", filter=Q(estado="inactivo", fecha_baja__isnull=True) | Q(fecha_baja__lt=F("fecha_alta")) | Q(estado="activo", fecha_baja__lte=timezone.localdate())),
    )
    datos["activos"] = activos_al_cierre(personas, periodo.hasta).count()
    segmentos = list(segmentos_periodo(periodo))
    diario = (periodo.hasta - periodo.desde).days < 31
    truncar = TruncDay if diario else TruncMonth

    def eventos(campo):
        filas = personas.filter(**{f"{campo}__range": (periodo.desde, periodo.hasta)}).order_by().annotate(
            punto=truncar(campo),
        ).values("punto").annotate(cantidad=Count("pk"))
        return {fila["punto"]: fila["cantidad"] for fila in filas}

    altas, bajas = eventos("fecha_alta"), eventos("fecha_baja")
    acumulado = personas.filter(fecha_alta__lt=periodo.desde).filter(Q(fecha_baja__isnull=True) | Q(fecha_baja__gte=periodo.desde)).count()
    serie = []
    for segmento in segmentos:
        clave = segmento.desde if diario else segmento.desde.replace(day=1)
        a, b = altas.get(clave, 0), bajas.get(clave, 0)
        acumulado += a - b
        serie.append({"desde": segmento.desde, "hasta": segmento.hasta,
            "etiqueta": segmento.hasta.strftime("%d/%m/%Y" if diario else "%m/%Y"),
            "activos": acumulado if not datos["inconsistentes"] else None, "altas": a, "bajas": b})
    if datos["inconsistentes"]:
        datos["activos"] = None
    datos.update(serie=serie, neto=datos["altas"] - datos["bajas"], diario=diario)
    return datos


def cuotas_del_periodo(periodo, tipo="todos"):
    cuotas = Cuota.objects.annotate(mes_ordinal=F("periodo__ciclo_lectivo__anio") * 12 + F("periodo__mes"))
    cuotas = cuotas.filter(mes_ordinal__range=(periodo.desde.year * 12 + periodo.desde.month, periodo.hasta.year * 12 + periodo.hasta.month))
    return cuotas if tipo == "todos" else cuotas.filter(asociado__tipo=tipo)


def cuotas_con_capital(cuotas, hoy):
    aplicaciones = PagoCuota.objects.filter(cuota_id=OuterRef("pk"), pago__fecha__lte=hoy).order_by().values("cuota_id").annotate(total=Sum("importe"))
    return cuotas.annotate(aplicado=Coalesce(Subquery(aplicaciones.values("total")), Value(Decimal("0")), output_field=DecimalField())).annotate(
        capital_cobrado=Round(Least(F("importe"), Greatest(F("aplicado"), Value(Decimal("0")))), precision=2),
        diferencia_aplicada=Round(F("importe_pagado") - F("aplicado"), precision=2),
    )


def metricas_cuotas(periodo, tipo="todos", hoy=None):
    hoy = hoy or timezone.localdate()
    cuotas = cuotas_con_capital(cuotas_del_periodo(periodo, tipo), hoy)
    datos = cuotas.aggregate(generado=Sum("importe", default=0), cobrado=Sum("capital_cobrado", default=0),
        cantidad=Count("pk"), personas=Count("asociado_id", distinct=True),
        inconsistentes=Count("pk", filter=~Q(diferencia_aplicada=0) | Q(importe__lt=0)))
    for campo in ("generado", "cobrado"):
        datos[campo] = Decimal(datos[campo]).quantize(Decimal("0.01"))
    datos["pendiente"] = datos["generado"] - datos["cobrado"]
    datos["cumplimiento"] = porcentaje(datos["cobrado"], datos["generado"])
    pendientes = cuotas.filter(capital_cobrado__lt=F("importe")).values("asociado_id")
    datos["personas_saldadas"] = cuotas.exclude(asociado_id__in=Subquery(pendientes)).values("asociado_id").distinct().count()
    filas = cuotas.order_by().values("periodo__ciclo_lectivo__anio", "periodo__mes").annotate(
        generado=Sum("importe"), cobrado=Sum("capital_cobrado"))
    por_mes = {(f["periodo__ciclo_lectivo__anio"], f["periodo__mes"]): f for f in filas}
    serie = []
    ordinal = periodo.desde.year * 12 + periodo.desde.month - 1
    fin = periodo.hasta.year * 12 + periodo.hasta.month - 1
    for mes in range(ordinal, fin + 1):
        anio, indice = divmod(mes, 12)
        fila = por_mes.get((anio, indice + 1), {"generado": Decimal(0), "cobrado": Decimal(0)})
        for campo in ("generado", "cobrado"):
            fila[campo] = Decimal(fila[campo]).quantize(Decimal("0.01"))
        serie.append({"etiqueta": f"{indice + 1:02d}/{anio}", "generado": fila["generado"], "cobrado": fila["cobrado"],
            "pendiente": fila["generado"] - fila["cobrado"], "cumplimiento": porcentaje(fila["cobrado"], fila["generado"])})
    datos["serie"] = serie
    return datos


def metricas_ingresos(periodo, tipo="todos"):
    pagos = Pago.objects.filter(fecha__range=(periodo.desde, periodo.hasta)).exclude(PAGO_HISTORICO)
    if tipo != "todos":
        pagos = pagos.filter(asociado__tipo=tipo)
    return resumir_pagos(pagos)


def cuotas_vencidas_metricas(tipo="todos", hoy=None):
    hoy = hoy or timezone.localdate()
    cuotas = Cuota.objects.filter(periodo__fecha_vencimiento__lt=hoy)
    if tipo != "todos":
        cuotas = cuotas.filter(asociado__tipo=tipo)
    return cuotas_con_saldo(cuotas, hoy).filter(saldo__gt=0)


def personas_con_estado_credencial(tipo="todos", hoy=None):
    hoy = hoy or timezone.localdate()
    deuda = cuotas_que_inactivan_credencial(hoy).filter(asociado_id=OuterRef("pk"))
    return personas_metricas(tipo).filter(estado=Asociado.ESTADO_ACTIVO).annotate(credencial_inactiva=Exists(deuda))


def metricas_credenciales(tipo="todos", hoy=None):
    personas = personas_con_estado_credencial(tipo, hoy)
    # Una sola consulta: agregados por tipo y clasificación, nunca por persona.
    filas = list(personas.order_by().values("tipo", "clasificacion_adherente__nombre").annotate(
        total=Count("pk"), inactivas=Count("pk", filter=Q(credencial_inactiva=True))))

    def resumen(filas):
        total = sum(f["total"] for f in filas)
        inactivas = sum(f["inactivas"] for f in filas)
        return {"total": total, "activas": total - inactivas, "inactivas": inactivas,
            "porcentaje": porcentaje(total - inactivas, total)}

    datos = resumen(filas)
    datos["por_tipo"] = [{"nombre": nombre, **resumen([f for f in filas if f["tipo"] == valor])}
        for valor, nombre in (("asociado", "Asociados"), ("adherente", "Adherentes")) if tipo in ("todos", valor)]
    datos["clasificaciones"] = [{"nombre": f["clasificacion_adherente__nombre"] or "Sin clasificar", **resumen([f])}
        for f in filas if f["tipo"] == "adherente"]
    datos["clasificaciones"].sort(key=lambda f: f["nombre"])
    return datos


def metricas_deuda(tipo="todos", hoy=None):
    hoy = hoy or timezone.localdate()
    cuotas = cuotas_vencidas_metricas(tipo, hoy)
    datos = cuotas.aggregate(total=Sum("saldo", default=0), recargos=Sum("recargo", default=0),
        cuotas=Count("pk"), personas=Count("asociado_id", distinct=True))
    por_persona = cuotas.order_by().values("asociado_id").annotate(numero=Count("pk"), total_persona=Sum("saldo"))
    grupos = []
    for numero, etiqueta in ((1, "1 cuota"), (2, "2 cuotas"), (3, "3+ cuotas")):
        grupo = por_persona.filter(numero__gte=3) if numero == 3 else por_persona.filter(numero=numero)
        agregado = grupo.aggregate(personas=Count("asociado_id"), total=Sum("total_persona", default=0))
        grupos.append({"grupo": numero, "etiqueta": etiqueta, **agregado})
    datos["grupos"] = grupos
    datos["antiguedad"] = []
    for etiqueta, filtro in (
        ("Hasta 30 días", Q(periodo__fecha_vencimiento__gte=hoy - timedelta(days=30))),
        ("31 a 60 días", Q(periodo__fecha_vencimiento__lt=hoy - timedelta(days=30), periodo__fecha_vencimiento__gte=hoy - timedelta(days=60))),
        ("Más de 60 días", Q(periodo__fecha_vencimiento__lt=hoy - timedelta(days=60))),
    ):
        datos["antiguedad"].append({"etiqueta": etiqueta, **cuotas.filter(filtro).aggregate(total=Sum("saldo", default=0))})
    return datos


def composicion_actual():
    activos = Asociado.objects.filter(estado=Asociado.ESTADO_ACTIVO)
    datos = activos.aggregate(total=Count("pk"), asociados=Count("pk", filter=Q(tipo="asociado")), adherentes=Count("pk", filter=Q(tipo="adherente")))
    datos["porcentaje_asociados"] = porcentaje(datos["asociados"], datos["total"])
    datos["porcentaje_adherentes"] = porcentaje(datos["adherentes"], datos["total"])
    datos["adherentes_por_cien"] = porcentaje(datos["adherentes"], datos["asociados"])
    filas = activos.filter(tipo="adherente").order_by("clasificacion_adherente__orden", "clasificacion_adherente__nombre").values(
        "clasificacion_adherente_id", "clasificacion_adherente__nombre").annotate(cantidad=Count("pk"))
    datos["clasificaciones"] = [{"id": f["clasificacion_adherente_id"], "nombre": f["clasificacion_adherente__nombre"] or "Sin clasificar",
        "cantidad": f["cantidad"], "porcentaje": porcentaje(f["cantidad"], datos["adherentes"])} for f in filas]
    return datos


def solicitudes_del_periodo(periodo, tipo="todos"):
    solicitudes = SolicitudAsociacion.objects.filter(creado_en__date__range=(periodo.desde, periodo.hasta))
    return solicitudes if tipo == "todos" else solicitudes.filter(tipo=tipo)


def metricas_solicitudes(periodo, tipo="todos"):
    filas = solicitudes_del_periodo(periodo, tipo).order_by().values("estado").annotate(cantidad=Count("pk"))
    cantidades = {f["estado"]: f["cantidad"] for f in filas}
    total = sum(cantidades.values())
    completadas = cantidades.get("alta_completada", 0)
    canceladas = cantidades.get("cancelada", 0)
    return {"total": total, "completadas": completadas, "canceladas": canceladas,
        "pendientes": total - completadas - canceladas, "conversion": porcentaje(completadas, total),
        "estados": [{"estado": estado, "nombre": nombre, "cantidad": cantidades.get(estado, 0)} for estado, nombre in SolicitudAsociacion.ESTADOS]}


def oferta_actual():
    comercios = Comercio.objects.filter(estado=Comercio.ESTADO_FIRMADO)
    return {"comercios": comercios.count(), "rubros": list(comercios.order_by("actividad_comercial__nombre").values(
        "actividad_comercial__nombre").annotate(cantidad=Count("pk")))}
