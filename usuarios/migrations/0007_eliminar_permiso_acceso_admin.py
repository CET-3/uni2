from django.db import migrations


def eliminar_permiso_acceso_admin(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")
    content_type = ContentType.objects.filter(
        app_label="usuarios", model="permisousuario"
    ).first()
    if content_type is None:
        return
    Permission.objects.filter(
        content_type=content_type, codename="acceder_admin_tecnico"
    ).delete()
    if not content_type.permission_set.exists():
        content_type.delete()


class Migration(migrations.Migration):
    dependencies = [("usuarios", "0006_reorganizar_grupos_operativos")]

    operations = [
        migrations.RunPython(eliminar_permiso_acceso_admin, migrations.RunPython.noop),
        migrations.DeleteModel(name="PermisoUsuario"),
    ]
