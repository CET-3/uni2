from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="PermisoGestion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ],
            options={
                "verbose_name": "Permiso de gestión",
                "verbose_name_plural": "Permisos de gestión",
                "permissions": [
                    ("ver_dashboard_gestion", "Puede ver el dashboard de gestión"),
                    ("consultar_asociados", "Puede consultar asociados"),
                    ("editar_asociados", "Puede editar asociados"),
                    ("importar_asociados", "Puede importar asociados"),
                    ("exportar_asociados", "Puede exportar asociados"),
                    ("cobrar_cuotas", "Puede cobrar cuotas"),
                    ("ver_deudores", "Puede ver deudores"),
                    ("administrar_periodos_cuota", "Puede administrar períodos de cuota"),
                    ("importar_cuotas_historicas", "Puede importar cuotas históricas"),
                ],
                "default_permissions": (),
                "managed": False,
            },
        ),
    ]
