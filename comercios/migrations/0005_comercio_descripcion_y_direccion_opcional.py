from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("comercios", "0004_comercio_foto"),
    ]

    operations = [
        migrations.AddField(
            model_name="comercio",
            name="descripcion",
            field=models.TextField(
                default="",
                help_text="Texto público que presenta la actividad o propuesta del comercio.",
                verbose_name="descripción",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="comercio",
            name="direccion",
            field=models.CharField(
                blank=True,
                help_text="Dirección física del comercio, si tiene un local o espacio de atención.",
                max_length=255,
                verbose_name="dirección",
            ),
        ),
        migrations.RemoveField(
            model_name="comercio",
            name="flyer_disponible",
        ),
        migrations.RemoveField(
            model_name="comercio",
            name="notas",
        ),
    ]
