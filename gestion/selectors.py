from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.utils import timezone

from asociados.models import Asociado
from comercios.selectors import get_comercios_con_beneficio
from cuotas.models import Cuota, Pago
from cuotas.selectors import get_total_deuda


def get_last_login_users():
    user_model = get_user_model()
    return user_model.objects.filter(last_login__isnull=False).order_by("-last_login")


def get_asociados_deudores():
    today = timezone.localdate()
    deudores = []
    for asociado in Asociado.objects.select_related("usuario", "curso_actual").order_by("apellido", "nombre"):
        deuda = get_total_deuda(asociado, today)
        if deuda > 0:
            deudores.append({"asociado": asociado, "deuda": deuda})
    deudores.sort(key=lambda item: item["deuda"], reverse=True)
    return deudores


def get_admin_dashboard_stats():
    today = timezone.localdate()
    asociados = Asociado.objects.select_related("usuario", "curso_actual").order_by("apellido", "nombre")
    cuotas = Cuota.objects.all()
    pagos_del_mes = Pago.objects.filter(fecha__year=today.year, fecha__month=today.month)
    deudores = get_asociados_deudores()

    cuotas_por_estado = {item["estado"]: item["total"] for item in cuotas.values("estado").annotate(total=Count("id"))}

    return {
        "resumen": {
            "asociados_activos": asociados.filter(estado=Asociado.ESTADO_ACTIVO).count(),
            "asociados_inactivos": asociados.filter(estado=Asociado.ESTADO_INACTIVO).count(),
            "asociados_egresados": asociados.filter(estado=Asociado.ESTADO_EGRESADO).count(),
            "asociados_sin_usuario": asociados.filter(usuario__isnull=True).count(),
            "asociados_con_usuario": asociados.filter(usuario__isnull=False).count(),
            "deudores": len(deudores),
            "cuotas_pendientes": cuotas_por_estado.get(Cuota.ESTADO_PENDIENTE, 0),
            "cuotas_vencidas": cuotas_por_estado.get(Cuota.ESTADO_VENCIDA, 0),
            "cuotas_parciales": cuotas_por_estado.get(Cuota.ESTADO_PARCIAL, 0),
            "cuotas_pagadas": cuotas_por_estado.get(Cuota.ESTADO_PAGADA, 0),
            "recaudacion_mes": pagos_del_mes.aggregate(total=Sum("importe"))["total"] or Decimal("0"),
            "comercios_con_beneficio": get_comercios_con_beneficio().count(),
        },
        "deudores": deudores[:5],
        "ultimos_accesos": asociados.filter(usuario__last_login__isnull=False).order_by("-usuario__last_login")[:5],
        "asociados_por_curso": asociados.exclude(curso_actual__isnull=True)
        .values("curso_actual__nombre")
        .annotate(total=Count("id"))
        .order_by("curso_actual__nombre"),
        "pagos_por_metodo": pagos_del_mes.values("metodo").annotate(total=Sum("importe")).order_by("metodo"),
    }

