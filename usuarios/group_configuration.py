"""Configuración repetible de los grupos administrados por Uni2."""

from dataclasses import dataclass, field

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db import transaction

from usuarios.roles import ACCESO_ADMIN_TECNICO, PERMISOS_POR_GRUPO


@dataclass
class GroupConfigurationResult:
    created_groups: list[str] = field(default_factory=list)
    changed_groups: list[str] = field(default_factory=list)
    missing_permissions: list[str] = field(default_factory=list)
    staff_enabled: int = 0
    staff_disabled: int = 0

    @property
    def has_drift(self):
        return bool(
            self.created_groups
            or self.changed_groups
            or self.missing_permissions
            or self.staff_enabled
            or self.staff_disabled
        )


def _permissions_by_natural_key():
    return {
        f"{permission.content_type.app_label}.{permission.codename}": permission
        for permission in Permission.objects.select_related("content_type")
    }


def _expected_staff_user_ids():
    """Calcula la capacidad futura sin depender de nombres escritos a mano."""

    user_model = get_user_model()
    admin_app, admin_codename = ACCESO_ADMIN_TECNICO.split(".", 1)
    managed_groups = set(PERMISOS_POR_GRUPO)
    configured_admin_groups = [
        group_name
        for group_name, permissions in PERMISOS_POR_GRUPO.items()
        if ACCESO_ADMIN_TECNICO in permissions
    ]
    user_ids = set(
        user_model.objects.filter(is_superuser=True).values_list("pk", flat=True)
    )
    user_ids.update(
        user_model.objects.filter(
            user_permissions__content_type__app_label=admin_app,
            user_permissions__codename=admin_codename,
        ).values_list("pk", flat=True)
    )
    user_ids.update(
        user_model.objects.filter(groups__name__in=configured_admin_groups).values_list(
            "pk", flat=True
        )
    )
    # Los grupos futuros quedan fuera de la matriz administrada, pero la
    # capacidad explícita sigue habilitando el admin.
    unmanaged_admin_group_ids = Group.objects.filter(
        permissions__content_type__app_label=admin_app,
        permissions__codename=admin_codename,
    ).exclude(name__in=managed_groups)
    user_ids.update(
        user_model.objects.filter(groups__in=unmanaged_admin_group_ids).values_list(
            "pk", flat=True
        )
    )
    return user_ids


def inspect_group_configuration():
    result = GroupConfigurationResult()
    available = _permissions_by_natural_key()

    for group_name, expected_names in PERMISOS_POR_GRUPO.items():
        group = Group.objects.filter(name=group_name).first()
        if group is None:
            result.created_groups.append(group_name)
        else:
            current_names = {
                f"{permission.content_type.app_label}.{permission.codename}"
                for permission in group.permissions.select_related("content_type")
            }
            if current_names != set(expected_names):
                result.changed_groups.append(group_name)
        result.missing_permissions.extend(
            name for name in expected_names if name not in available
        )

    user_model = get_user_model()
    staff_ids = _expected_staff_user_ids()
    result.staff_enabled = user_model.objects.filter(
        pk__in=staff_ids, is_staff=False
    ).count()
    result.staff_disabled = (
        user_model.objects.filter(is_staff=True, is_superuser=False)
        .exclude(pk__in=staff_ids)
        .count()
    )
    return result


@transaction.atomic
def sync_group_configuration():
    before = inspect_group_configuration()
    if before.missing_permissions:
        missing = ", ".join(sorted(set(before.missing_permissions)))
        raise ValueError(f"Faltan permisos Django requeridos: {missing}")

    available = _permissions_by_natural_key()
    for group_name, expected_names in PERMISOS_POR_GRUPO.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        group.permissions.set(available[name] for name in expected_names)

    user_model = get_user_model()
    staff_ids = _expected_staff_user_ids()
    user_model.objects.filter(pk__in=staff_ids).update(is_staff=True)
    user_model.objects.filter(is_staff=True, is_superuser=False).exclude(
        pk__in=staff_ids
    ).update(is_staff=False)
    return before
