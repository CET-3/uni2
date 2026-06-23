from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("comercios", "0002_alter_comercio_ciudad_alter_comercio_email_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="comercio",
            name="orden",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Posición usada para ordenar los comercios publicados.",
                verbose_name="orden",
            ),
        ),
        migrations.AlterModelOptions(
            name="comercio",
            options={
                "ordering": ["orden", "nombre"],
                "verbose_name": "Comercio",
                "verbose_name_plural": "Comercios",
            },
        ),
        migrations.RemoveIndex(
            model_name="comercio",
            name="comercios_c_estado_a6d043_idx",
        ),
        migrations.AddIndex(
            model_name="comercio",
            index=models.Index(
                fields=["estado", "orden", "nombre"],
                name="comercios_c_estado_bd1d68_idx",
            ),
        ),
    ]
