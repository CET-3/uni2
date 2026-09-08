from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission, User
from django.test import RequestFactory

import pytest

import usuarios.admin  # noqa: F401
from usuarios.roles import (
    ADMINISTRADOR_APP_GROUP,
    ADMINISTRADOR_PERMISOS_GROUP,
    ASOCIADO_GROUP,
    COMERCIO_GROUP,
)


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


@pytest.mark.django_db
def test_usuario_con_add_group_puede_crear_grupo():
    operador = get_user_model().objects.create_user(
        username="creador-grupos", password="secreto123"
    )
    operador.user_permissions.add(
        Permission.objects.get(content_type__app_label="auth", codename="add_group")
    )
    request = RequestFactory().get("/admin/auth/group/add/")
    request.user = operador
    group_admin = admin.site._registry[Group]

    assert group_admin.has_add_permission(request)


@pytest.mark.django_db
def test_usuario_con_delete_group_puede_borrar_grupo():
    operador = get_user_model().objects.create_user(
        username="borrador-grupos", password="secreto123"
    )
    operador.user_permissions.add(
        Permission.objects.get(content_type__app_label="auth", codename="delete_group")
    )
    grupo = Group.objects.create(name="Grupo para borrar")
    request = RequestFactory().get(f"/admin/auth/group/{grupo.pk}/delete/")
    request.user = operador
    group_admin = admin.site._registry[Group]

    assert group_admin.has_delete_permission(request, grupo)


@pytest.mark.django_db
def test_usuario_con_change_group_puede_editar_grupo_personalizado():
    operador = get_user_model().objects.create_user(username="rrhh", password="secreto123")
    operador.user_permissions.add(
        Permission.objects.get(content_type__app_label="auth", codename="change_group")
    )
    grupo = Group.objects.create(name="Recursos Humanos y Coordinación")
    request = RequestFactory().get(f"/admin/auth/group/{grupo.pk}/change/")
    request.user = operador
    group_admin = admin.site._registry[Group]

    assert group_admin.has_change_permission(request, grupo)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "nombre_grupo",
    [ADMINISTRADOR_APP_GROUP, ASOCIADO_GROUP, COMERCIO_GROUP],
)
def test_usuario_con_change_group_puede_editar_cualquier_grupo(nombre_grupo):
    operador = get_user_model().objects.create_user(
        username=f"rrhh-{nombre_grupo}", password="secreto123"
    )
    operador.user_permissions.add(
        Permission.objects.get(content_type__app_label="auth", codename="change_group")
    )
    grupo = Group.objects.get(name=nombre_grupo)
    request = RequestFactory().get(f"/admin/auth/group/{grupo.pk}/change/")
    request.user = operador
    group_admin = admin.site._registry[Group]

    assert group_admin.has_change_permission(request, grupo)


@pytest.mark.django_db
def test_usuario_sin_change_group_no_edita_grupo_personalizado():
    operador = get_user_model().objects.create_user(username="sin-permiso", password="secreto123")
    grupo = Group.objects.create(name="Grupo personalizado")
    request = RequestFactory().get(f"/admin/auth/group/{grupo.pk}/change/")
    request.user = operador
    group_admin = admin.site._registry[Group]

    assert not group_admin.has_change_permission(request, grupo)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "nombre_grupo",
    [ADMINISTRADOR_APP_GROUP, ASOCIADO_GROUP, COMERCIO_GROUP],
)
def test_superusuario_edita_grupos_tecnicos(nombre_grupo):
    superusuario = get_user_model().objects.create_superuser(
        username=f"root-{nombre_grupo}", password="secreto123", email="root@example.com"
    )
    grupo = Group.objects.get(name=nombre_grupo)
    request = RequestFactory().get(f"/admin/auth/group/{grupo.pk}/change/")
    request.user = superusuario
    group_admin = admin.site._registry[Group]

    assert group_admin.has_change_permission(request, grupo)
