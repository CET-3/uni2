from django.db import migrations, models
import django.db.models.deletion


def cargar_actividad_comercial_default(apps, schema_editor):
    ActividadComercial = apps.get_model("comercios", "ActividadComercial")
    Comercio = apps.get_model("comercios", "Comercio")

    general, _ = ActividadComercial.objects.get_or_create(nombre="General", defaults={"activo": True})
    Comercio.objects.filter(actividad_comercial__isnull=True).update(actividad_comercial=general)


class Migration(migrations.Migration):
    dependencies = [
        ("comercios", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ActividadComercial",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=100, unique=True)),
                ("activo", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Actividad comercial",
                "verbose_name_plural": "Actividades comerciales",
                "ordering": ["nombre"],
            },
        ),
        migrations.AddField(
            model_name="comercio",
            name="actividad_comercial",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="comercios",
                to="comercios.actividadcomercial",
            ),
        ),
        migrations.AddField(
            model_name="comercio",
            name="beneficio_texto",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="comercio",
            name="estado",
            field=models.CharField(
                choices=[
                    ("pendiente", "Pendiente"),
                    ("firmado", "Firmado"),
                    ("vencido", "Vencido"),
                    ("baja", "Baja"),
                ],
                default="pendiente",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="comercio",
            name="fecha_convenio",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="comercio",
            name="flyer_disponible",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="comercio",
            name="notas",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="comercio",
            name="propietario",
            field=models.CharField(blank=True, default="", max_length=150),
            preserve_default=False,
        ),
        migrations.RunPython(cargar_actividad_comercial_default, migrations.RunPython.noop),
        migrations.RemoveField(model_name="comercio", name="responsable"),
        migrations.DeleteModel(name="BeneficioComercio"),
    ]
