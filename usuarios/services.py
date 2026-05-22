from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction

from asociados.models import Asociado


ADMIN_GROUP = "Administradores"
ASOCIADO_GROUP = "Asociados"
COMERCIO_GROUP = "Comercios"
DEFAULT_GROUPS = (ADMIN_GROUP, ASOCIADO_GROUP, COMERCIO_GROUP)


def ensure_default_groups():
    for group_name in DEFAULT_GROUPS:
        Group.objects.get_or_create(name=group_name)


def user_has_group(user, group_name: str) -> bool:
    return user.is_authenticated and user.groups.filter(name=group_name).exists()


def user_is_asociado(user) -> bool:
    return user_has_group(user, ASOCIADO_GROUP) or hasattr(user, "asociado")


def user_is_comercio(user) -> bool:
    return user_has_group(user, COMERCIO_GROUP) or hasattr(user, "comercio")


@transaction.atomic
def create_user_for_asociado(asociado: Asociado, password: str, email: str | None = None):
    if asociado.usuario_id:
        raise ValueError("El asociado ya tiene un usuario vinculado.")

    user_model = get_user_model()
    username = str(asociado.dni)
    if user_model.objects.filter(username=username).exists():
        raise ValueError("Ya existe un usuario con ese username.")

    user = user_model.objects.create_user(
        username=username,
        email=email or asociado.email,
        password=password,
        first_name=asociado.nombre,
        last_name=asociado.apellido,
        is_active=True,
    )
    asociado.usuario = user
    asociado.save(update_fields=["usuario"])
    group = Group.objects.get(name=ASOCIADO_GROUP)
    user.groups.add(group)
    return user
