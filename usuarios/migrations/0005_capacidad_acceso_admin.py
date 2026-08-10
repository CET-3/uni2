from django.db import migrations, models


GRUPOS_INICIALES_CON_ACCESO = (
    "Administrador de permisos",
    "Gestión de convenios",
    "Gestión de publicidades",
    "Administrador de la mutual",
)


def configurar_capacidad(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    User = apps.get_model("auth", "User")

    content_type, _ = ContentType.objects.get_or_create(
        app_label="usuarios",
        model="permisousuario",
    )
    permiso, _ = Permission.objects.get_or_create(
        content_type=content_type,
        codename="acceder_admin_tecnico",
        defaults={"name": "Puede acceder al admin técnico"},
    )
    grupos = Group.objects.filter(name__in=GRUPOS_INICIALES_CON_ACCESO)
    for grupo in grupos:
        grupo.permissions.add(permiso)

    User.objects.filter(groups__permissions=permiso).distinct().update(is_staff=True)


class Migration(migrations.Migration):
    dependencies = [("usuarios", "0004_configurar_grupos_iniciales")]

    operations = [
        migrations.CreateModel(
            name="PermisoUsuario",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={
                "verbose_name": "Permiso de usuario",
                "verbose_name_plural": "Permisos de usuario",
                "permissions": [
                    ("acceder_admin_tecnico", "Puede acceder al admin técnico"),
                ],
                "default_permissions": (),
                "managed": False,
            },
        ),
        migrations.RunPython(configurar_capacidad, migrations.RunPython.noop),
    ]
