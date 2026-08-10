from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("auditoria", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="eventoauditoria",
            name="actor_etiqueta",
            field=models.CharField(
                help_text=(
                    "Copia del nombre visible al registrar el evento. Permanece "
                    "aunque la cuenta cambie o deje de existir."
                ),
                max_length=150,
                verbose_name="nombre registrado del actor",
            ),
        ),
    ]
