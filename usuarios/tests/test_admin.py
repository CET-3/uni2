from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.test import RequestFactory

import pytest

import usuarios.admin  # noqa: F401
from usuarios.roles import ADMINISTRADOR_APP_GROUP, ADMINISTRADOR_PERMISOS_GROUP


class FakeGroups:
    def order_by(self, field_name):
        return self

    def values_list(self, field_name, flat=False):
        return ["Administrador de la app", "Asociados"]


class FakeUser:
    groups = FakeGroups()


def test_user_admin_muestra_grupos():
    user_admin = admin.site._registry[User]

    assert "mostrar_grupos" in user_admin.list_display
    assert user_admin.mostrar_grupos(FakeUser()) == "Administrador de la app, Asociados"


@pytest.mark.django_db
def test_administrador_permisos_no_puede_editar_superusuarios_o_admin_app():
    user_model = get_user_model()
    operador = user_model.objects.create_user(
        username="permisos", password="secreto123", is_staff=True
    )
    operador.groups.add(operador.groups.model.objects.get(name=ADMINISTRADOR_PERMISOS_GROUP))
    superusuario = user_model.objects.create_superuser(
        username="root", password="secreto123", email="root@example.com"
    )
    admin_app = user_model.objects.create_user(username="tecnico", password="secreto123")
    admin_app.groups.add(admin_app.groups.model.objects.get(name=ADMINISTRADOR_APP_GROUP))
    usuario_normal = user_model.objects.create_user(username="normal", password="secreto123")
    request = RequestFactory().get("/admin/auth/user/")
    request.user = operador
    user_admin = admin.site._registry[User]

    assert user_admin.has_change_permission(request, usuario_normal)
    assert not user_admin.has_change_permission(request, superusuario)
    assert not user_admin.has_change_permission(request, admin_app)


@pytest.mark.django_db
def test_administrador_permisos_no_puede_asignar_grupo_admin_app():
    user_model = get_user_model()
    operador = user_model.objects.create_user(
        username="permisos_grupos", password="secreto123", is_staff=True
    )
    operador.groups.add(operador.groups.model.objects.get(name=ADMINISTRADOR_PERMISOS_GROUP))
    request = RequestFactory().get("/admin/auth/user/add/")
    request.user = operador
    user_admin = admin.site._registry[User]

    campo = user_admin.formfield_for_manytomany(User._meta.get_field("groups"), request)

    assert not campo.queryset.filter(name=ADMINISTRADOR_APP_GROUP).exists()
