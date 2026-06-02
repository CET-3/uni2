from .models import Beneficio


def create_beneficio(**kwargs):
    return Beneficio.objects.create(**kwargs)
