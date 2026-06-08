from django.contrib import admin
from django.contrib.auth.models import User

import usuarios.admin  # noqa: F401


class FakeGroups:
    def order_by(self, field_name):
        return self

    def values_list(self, field_name, flat=False):
        return ["Administradores", "Asociados"]


class FakeUser:
    groups = FakeGroups()


def test_user_admin_muestra_grupos():
    user_admin = admin.site._registry[User]

    assert "mostrar_grupos" in user_admin.list_display
    assert user_admin.mostrar_grupos(FakeUser()) == "Administradores, Asociados"
