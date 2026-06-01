from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("comercios", "0003_remove_comercio_activo"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="actividadcomercial",
            name="activo",
        ),
    ]
