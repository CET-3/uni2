from django.utils import timezone

from asociados.models import Asociado
from cuotas.selectors import get_total_deuda


def get_asociados_deudores():
    today = timezone.localdate()
    deudores = []
    for asociado in Asociado.objects.select_related("usuario", "curso_actual").order_by("apellido", "nombre"):
        deuda = get_total_deuda(asociado, today)
        if deuda > 0:
            deudores.append({"asociado": asociado, "deuda": deuda})
    deudores.sort(key=lambda item: item["deuda"], reverse=True)
    return deudores
