from django.db import migrations, models
from django.utils import timezone


def marcar_periodos_con_cuotas(apps, schema_editor):
    Cuota = apps.get_model("cuotas", "Cuota")
    PeriodoCuota = apps.get_model("cuotas", "PeriodoCuota")
    periodo_ids = Cuota.objects.values_list("periodo_id", flat=True).distinct()
    PeriodoCuota.objects.filter(pk__in=periodo_ids).update(generado_el=timezone.now())


class Migration(migrations.Migration):

    dependencies = [
        ("cuotas", "0004_alter_cuota_estado"),
    ]

    operations = [
        migrations.AddField(
            model_name="periodocuota",
            name="generado_el",
            field=models.DateTimeField(
                blank=True,
                editable=False,
                help_text=(
                    "Fecha y hora de la primera ejecución de la generación masiva de cuotas."
                ),
                null=True,
                verbose_name="generado el",
            ),
        ),
        migrations.RunPython(marcar_periodos_con_cuotas, migrations.RunPython.noop),
    ]
