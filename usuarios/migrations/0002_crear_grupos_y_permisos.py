from django.db import migrations


def crear_grupos_y_permisos(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    admin_group, _ = Group.objects.get_or_create(name="Administradores")
    atencion_group, _ = Group.objects.get_or_create(name="Atención de mutual")
    Group.objects.get_or_create(name="Asociados")
    Group.objects.get_or_create(name="Comercios")

    gestion_perms = Permission.objects.filter(
        content_type__app_label="gestion",
    )

    admin_group.permissions.add(*gestion_perms)

    atencion_codenames = [
        "ver_dashboard_gestion",
        "consultar_asociados",
        "editar_asociados",
        "cobrar_cuotas",
    ]
    atencion_perms = gestion_perms.filter(codename__in=atencion_codenames)
    atencion_group.permissions.add(*atencion_perms)


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0001_initial"),
        ("gestion", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(crear_grupos_y_permisos),
    ]
