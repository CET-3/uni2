# Generated manually for the internal design system permission.

from django.db import migrations


PERMISSION_CODENAME = "ver_design_system"
PERMISSION_NAME = "Puede ver el design system del proyecto"
GROUP_NAMES = ["Administradores", "Atención de mutual"]


def asignar_permiso_design_system(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    content_type, _ = ContentType.objects.get_or_create(
        app_label="gestion",
        model="permisogestion",
    )
    permission, _ = Permission.objects.get_or_create(
        content_type=content_type,
        codename=PERMISSION_CODENAME,
        defaults={"name": PERMISSION_NAME},
    )

    for group_name in GROUP_NAMES:
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            continue
        group.permissions.add(permission)


def quitar_permiso_design_system(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    try:
        content_type = ContentType.objects.get(app_label="gestion", model="permisogestion")
        permission = Permission.objects.get(content_type=content_type, codename=PERMISSION_CODENAME)
    except (ContentType.DoesNotExist, Permission.DoesNotExist):
        return

    for group_name in GROUP_NAMES:
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            continue
        group.permissions.remove(permission)


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("gestion", "0002_alter_permisogestion_options"),
        ("usuarios", "0002_crear_grupos_y_permisos"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="permisogestion",
            options={
                "default_permissions": (),
                "managed": False,
                "permissions": [
                    ("ver_dashboard_gestion", "Puede ver el dashboard de gestión"),
                    ("consultar_asociados", "Puede consultar asociados"),
                    ("editar_asociados", "Puede editar asociados"),
                    ("importar_asociados", "Puede importar asociados"),
                    ("exportar_asociados", "Puede exportar asociados"),
                    ("cobrar_cuotas", "Puede cobrar cuotas"),
                    ("ver_deudores", "Puede ver deudores"),
                    ("administrar_periodos_cuota", "Puede administrar períodos de cuota"),
                    ("importar_cuotas_historicas", "Puede importar cuotas históricas"),
                    ("ver_especificacion", "Puede ver la especificación del proyecto"),
                    ("ver_design_system", "Puede ver el design system del proyecto"),
                ],
                "verbose_name": "Permiso de gestión",
                "verbose_name_plural": "Permisos de gestión",
            },
        ),
        migrations.RunPython(asignar_permiso_design_system, quitar_permiso_design_system),
    ]
