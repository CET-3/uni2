"""Configuración repetible de los grupos administrados por Uni2."""

from dataclasses import dataclass, field

from django.contrib.auth.models import Group, Permission
from django.db import transaction

from usuarios.roles import PERMISOS_POR_GRUPO


@dataclass
class GroupConfigurationResult:
    created_groups: list[str] = field(default_factory=list)
    changed_groups: list[str] = field(default_factory=list)
    missing_permissions: list[str] = field(default_factory=list)

    @property
    def has_drift(self):
        return bool(
            self.created_groups
            or self.changed_groups
            or self.missing_permissions
        )


def _permissions_by_natural_key():
    return {
        f"{permission.content_type.app_label}.{permission.codename}": permission
        for permission in Permission.objects.select_related("content_type")
    }


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

    return before
