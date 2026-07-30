from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("comercios", "0005_comercio_descripcion_y_direccion_opcional"),
    ]

    operations = [
        migrations.AddField(
            model_name="actividadcomercial",
            name="descripcion",
            field=models.TextField(
                blank=True,
                help_text="Texto público que presenta el rubro en la página de beneficios.",
                verbose_name="descripción",
            ),
        ),
    ]
