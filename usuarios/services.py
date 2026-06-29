from dataclasses import dataclass, field

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction

from asociados.models import Asociado
from comercios.models import Comercio
from gestion.permissions import user_has_any_gestion_permission


ADMIN_GROUP = "Administradores"
ATENCION_MUTUAL_GROUP = "Atención de mutual"
ASOCIADO_GROUP = "Asociados"
COMERCIO_GROUP = "Comercios"
DEFAULT_GROUPS = (ADMIN_GROUP, ATENCION_MUTUAL_GROUP, ASOCIADO_GROUP, COMERCIO_GROUP)


@dataclass
class MissingAsociadoUsersResult:
    creados: int = 0
    vinculados: int = 0
    omitidos: int = 0
    procesados: int = 0
    restantes: int = 0
    siguiente_cursor: int | None = None
    hay_mas: bool = False
    errores: list[str] = field(default_factory=list)


def ensure_default_groups():
    for group_name in DEFAULT_GROUPS:
        Group.objects.get_or_create(name=group_name)


def user_has_group(user, group_name: str) -> bool:
    return user.is_authenticated and user.groups.filter(name=group_name).exists()


def user_is_asociado(user) -> bool:
    return user_has_group(user, ASOCIADO_GROUP) or hasattr(user, "asociado")


def user_is_comercio(user) -> bool:
    return user_has_group(user, COMERCIO_GROUP) or hasattr(user, "comercio")


def user_has_gestion_access(user) -> bool:
    return user_has_any_gestion_permission(user)


def get_available_experiences(user) -> list[str]:
    if not user.is_authenticated:
        return []

    experiences = []
    if hasattr(user, "asociado"):
        experiences.append("asociado")
    if hasattr(user, "comercio"):
        experiences.append("comercio")
    if user_has_gestion_access(user):
        experiences.append("gestion")
    return experiences


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


def create_missing_users_for_asociados(batch_size: int | None = None, after_id: int = 0) -> MissingAsociadoUsersResult:
    result = MissingAsociadoUsersResult()
    result.omitidos = Asociado.objects.filter(usuario__isnull=False).count()
    asociados_qs = Asociado.objects.filter(usuario__isnull=True, id__gt=after_id).order_by("id")
    total_pendientes = asociados_qs.count()
    asociados = list(asociados_qs if batch_size is None else asociados_qs[:batch_size])
    result.procesados = len(asociados)
    result.restantes = max(total_pendientes - result.procesados, 0)
    result.hay_mas = result.restantes > 0
    if not asociados:
        return result

    user_model = get_user_model()
    asociado_group = Group.objects.get(name=ASOCIADO_GROUP)
    usuarios_existentes = user_model.objects.filter(username__in=[str(asociado.dni) for asociado in asociados])
    usuarios_existentes = {user.username: user for user in usuarios_existentes}

    for asociado in asociados:
        username = str(asociado.dni)
        existing_user = usuarios_existentes.get(username)
        if existing_user is not None:
            if hasattr(existing_user, "asociado"):
                result.errores.append(f"Asociado {asociado.dni}: el usuario existente ya está vinculado a otro asociado.")
                continue
            asociado.usuario = existing_user
            asociado.save(update_fields=["usuario"])
            existing_user.groups.add(asociado_group)
            result.vinculados += 1
            continue

        try:
            create_user_for_asociado(asociado=asociado, password=username)
        except ValueError as exc:
            result.errores.append(f"Asociado {asociado.dni}: {exc}")
        else:
            result.creados += 1

    if asociados and result.hay_mas:
        result.siguiente_cursor = asociados[-1].id
    return result


@transaction.atomic
def create_user_for_comercio(comercio: Comercio, password: str, email: str | None = None):
    if comercio.usuario_id:
        raise ValueError("El comercio ya tiene un usuario vinculado.")

    user_model = get_user_model()
    username = f"com-{comercio.id}"
    if user_model.objects.filter(username=username).exists():
        raise ValueError("Ya existe un usuario con ese username.")

    user = user_model.objects.create_user(
        username=username,
        email=email or comercio.email or "",
        password=password,
        first_name=comercio.nombre,
        last_name="",
        is_active=True,
    )
    comercio.usuario = user
    comercio.save(update_fields=["usuario"])
    group = Group.objects.get(name=COMERCIO_GROUP)
    user.groups.add(group)
    return user
