from django.db import migrations


PERMISSION_CODENAME = "ver_movimientos_asociado"
PERMISSION_NAME = "Puede ver los movimientos de la ficha del asociado"
GROUPS_WITH_PERMISSION = (
    "Atención al asociado",
    "Administrador de la mutual",
)


def crear_y_asignar_permiso(apps, schema_editor):
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
    for group in Group.objects.filter(name__in=GROUPS_WITH_PERMISSION):
        group.permissions.add(permission)


def quitar_permiso(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    Permission.objects.filter(
        content_type__app_label="gestion",
        content_type__model="permisogestion",
        codename=PERMISSION_CODENAME,
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("gestion", "0004_agregar_permiso_auditoria"),
        ("usuarios", "0005_capacidad_acceso_admin"),
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
                    ("ver_movimientos_asociado", "Puede ver los movimientos de la ficha del asociado"),
                ],
                "verbose_name": "Permiso de gestión",
                "verbose_name_plural": "Permisos de gestión",
            },
        ),
        migrations.RunPython(crear_y_asignar_permiso, quitar_permiso),
    ]
