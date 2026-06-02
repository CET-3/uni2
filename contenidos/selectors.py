from .models import Beneficio


def get_beneficios_publicos():
    return Beneficio.objects.filter(activo=True)
