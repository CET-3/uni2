from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from asociados.models import Asociado


def get_user_groups():
    return Group.objects.order_by("name")


def get_asociados_with_user_status():
    return Asociado.objects.select_related("usuario", "curso_actual").order_by("apellido", "nombre")


def get_last_login_users():
    user_model = get_user_model()
    return user_model.objects.filter(last_login__isnull=False).order_by("-last_login")

