from django.db import migrations


PERMISSION_CODENAME = "ver_auditoria"
PERMISSION_NAME = "Puede ver la auditoría de gestión"
ADMIN_GROUP = "Administradores"


def asignar_permiso_auditoria(apps, schema_editor):
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

    try:
        administradores = Group.objects.get(name=ADMIN_GROUP)
    except Group.DoesNotExist:
        return
    administradores.permissions.add(permission)


def quitar_permiso_auditoria(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    try:
        content_type = ContentType.objects.get(
            app_label="gestion",
            model="permisogestion",
        )
        permission = Permission.objects.get(
            content_type=content_type,
            codename=PERMISSION_CODENAME,
        )
        administradores = Group.objects.get(name=ADMIN_GROUP)
    except (ContentType.DoesNotExist, Permission.DoesNotExist, Group.DoesNotExist):
        return
    administradores.permissions.remove(permission)


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("gestion", "0003_alter_permisogestion_options"),
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
                    ("ver_auditoria", "Puede ver la auditoría de gestión"),
                ],
                "verbose_name": "Permiso de gestión",
                "verbose_name_plural": "Permisos de gestión",
            },
        ),
        migrations.RunPython(asignar_permiso_auditoria, quitar_permiso_auditoria),
    ]
