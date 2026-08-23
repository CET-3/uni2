import django.db.models.deletion
from django.db import migrations, models


CLASIFICACIONES_INICIALES = (
    "Docente",
    "Preceptor",
    "Directivo",
    "Auxiliar",
    "Biblioteca",
    "Padrino mutual",
    "Particular",
    "Familiar",
    "Estudiante",
    "Sin clasificar",
)


def crear_clasificaciones_y_completar_adherentes(apps, schema_editor):
    Asociado = apps.get_model("asociados", "Asociado")
    Clasificacion = apps.get_model("asociados", "ClasificacionAdherente")
    creadas = {}
    for orden, nombre in enumerate(CLASIFICACIONES_INICIALES, start=1):
        creadas[nombre], _ = Clasificacion.objects.get_or_create(
            nombre=nombre,
            defaults={"orden": orden, "activa": True},
        )
    Asociado.objects.filter(tipo="adherente", clasificacion_adherente__isnull=True).update(
        clasificacion_adherente=creadas["Sin clasificar"]
    )


class Migration(migrations.Migration):
    dependencies = [("asociados", "0007_remove_estado_egresado")]

    operations = [
        migrations.CreateModel(
            name="ClasificacionAdherente",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(help_text="Nombre visible de la clasificación del adherente.", max_length=100, unique=True, verbose_name="nombre")),
                ("activa", models.BooleanField(default=True, help_text="Indica si puede asignarse en nuevas altas y ediciones.", verbose_name="activa")),
                ("orden", models.PositiveIntegerField(default=0, help_text="Posición en formularios y listados.", verbose_name="orden")),
            ],
            options={
                "verbose_name": "Clasificación de adherente",
                "verbose_name_plural": "Clasificaciones de adherentes",
                "ordering": ["orden", "nombre"],
            },
        ),
        migrations.AddField(
            model_name="asociado",
            name="clasificacion_adherente",
            field=models.ForeignKey(
                blank=True,
                help_text="Clasificación institucional; corresponde únicamente a adherentes.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="adherentes",
                to="asociados.clasificacionadherente",
                verbose_name="clasificación de adherente",
            ),
        ),
        migrations.RunPython(crear_clasificaciones_y_completar_adherentes, migrations.RunPython.noop),
    ]
