from django.db import migrations, models


def convertir_egresados_en_inactivos(apps, schema_editor):
    Asociado = apps.get_model("asociados", "Asociado")
    Asociado.objects.filter(estado="egresado").update(estado="inactivo")


class Migration(migrations.Migration):

    dependencies = [
        ("asociados", "0006_remove_asociado_fecha_nacimiento_asociado_direccion"),
    ]

    operations = [
        migrations.RunPython(convertir_egresados_en_inactivos, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="asociado",
            name="estado",
            field=models.CharField(
                choices=[("activo", "Activo"), ("inactivo", "Inactivo")],
                default="activo",
                max_length=20,
            ),
        ),
    ]
