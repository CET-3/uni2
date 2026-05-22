from .models import Asiento


def get_asientos():
    return Asiento.objects.order_by("-fecha", "-id")

