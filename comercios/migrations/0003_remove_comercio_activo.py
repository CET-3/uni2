from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("comercios", "0002_refactor_comercios_mvp"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="comercio",
            name="activo",
        ),
    ]
