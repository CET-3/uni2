from django.db import migrations


ATENCION = "Atención al asociado"
PERMISOS = "Administrador de permisos"
CONVENIOS = "Gestión de convenios"
PUBLICIDADES = "Gestión de publicidades"
MUTUAL = "Administrador de la mutual"
APP = "Administrador de la app"

PERMISOS_POR_GRUPO = {
    ATENCION: (
        "gestion.ver_dashboard_gestion", "gestion.consultar_asociados",
        "gestion.editar_asociados", "gestion.cobrar_cuotas",
    ),
    PERMISOS: (
        "gestion.ver_dashboard_gestion", "gestion.ver_auditoria",
        "auth.view_user", "auth.add_user", "auth.change_user", "auth.view_group",
        "auditoria.view_eventoauditoria",
    ),
    CONVENIOS: (
        "gestion.ver_dashboard_gestion",
        "comercios.view_actividadcomercial", "comercios.add_actividadcomercial",
        "comercios.change_actividadcomercial", "comercios.view_comercio",
        "comercios.add_comercio", "comercios.change_comercio",
    ),
    PUBLICIDADES: (
        "gestion.ver_dashboard_gestion",
        "contenidos.view_categoriaproductoservicio", "contenidos.add_categoriaproductoservicio",
        "contenidos.change_categoriaproductoservicio", "contenidos.view_productoservicio",
        "contenidos.add_productoservicio", "contenidos.change_productoservicio",
        "contenidos.view_publicidad", "contenidos.add_publicidad",
        "contenidos.change_publicidad", "comercios.view_comercio",
    ),
    MUTUAL: (
        "gestion.ver_dashboard_gestion", "gestion.consultar_asociados",
        "gestion.editar_asociados", "gestion.exportar_asociados",
        "gestion.cobrar_cuotas", "gestion.ver_deudores",
        "gestion.administrar_periodos_cuota", "gestion.ver_especificacion",
        "gestion.ver_auditoria",
        "asociados.view_asociado", "asociados.add_asociado", "asociados.change_asociado",
        "asociados.view_ciclolectivo", "asociados.add_ciclolectivo",
        "asociados.change_ciclolectivo", "asociados.view_curso",
        "asociados.add_curso", "asociados.change_curso",
        "comercios.view_actividadcomercial", "comercios.add_actividadcomercial",
        "comercios.change_actividadcomercial", "comercios.view_comercio",
        "comercios.add_comercio", "comercios.change_comercio",
        "contenidos.view_categoriaproductoservicio", "contenidos.add_categoriaproductoservicio",
        "contenidos.change_categoriaproductoservicio", "contenidos.view_productoservicio",
        "contenidos.add_productoservicio", "contenidos.change_productoservicio",
        "contenidos.view_publicidad", "contenidos.add_publicidad",
        "contenidos.change_publicidad",
        "cuotas.view_periodocuota", "cuotas.add_periodocuota", "cuotas.change_periodocuota",
        "cuotas.view_cuota", "cuotas.view_pago", "cuotas.view_pagocuota",
        "cuotas.view_donacion", "auditoria.view_eventoauditoria", "auth.view_user",
    ),
}


def _renombrar_o_unir_grupo(Group, anterior, nuevo):
    grupo_anterior = Group.objects.filter(name=anterior).first()
    grupo_nuevo = Group.objects.filter(name=nuevo).first()
    if grupo_anterior is None:
        return grupo_nuevo or Group.objects.create(name=nuevo)
    if grupo_nuevo is None:
        grupo_anterior.name = nuevo
        grupo_anterior.save(update_fields=["name"])
        return grupo_anterior
    for usuario in grupo_anterior.user_set.all():
        usuario.groups.add(grupo_nuevo)
    grupo_anterior.delete()
    return grupo_nuevo


def configurar_grupos(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    _renombrar_o_unir_grupo(Group, "Administradores", APP)
    _renombrar_o_unir_grupo(Group, "Atención de mutual", ATENCION)
    for nombre in (*PERMISOS_POR_GRUPO, APP, "Asociados", "Comercios"):
        Group.objects.get_or_create(name=nombre)

    for nombre_grupo, permisos_naturales in PERMISOS_POR_GRUPO.items():
        permisos = []
        for permiso_natural in permisos_naturales:
            app_label, codename = permiso_natural.split(".", 1)
            model = "permisogestion" if app_label == "gestion" else codename.split("_", 1)[1]
            content_type, _ = ContentType.objects.get_or_create(
                app_label=app_label,
                model=model,
            )
            permiso, _ = Permission.objects.get_or_create(
                content_type=content_type,
                codename=codename,
                defaults={"name": codename.replace("_", " ").capitalize()},
            )
            permisos.append(permiso)
        Group.objects.get(name=nombre_grupo).permissions.set(permisos)

    # Es una etiqueta para superusuarios, no una forma de obtener privilegios.
    Group.objects.get(name=APP).permissions.clear()


class Migration(migrations.Migration):
    dependencies = [
        ("asociados", "0007_remove_estado_egresado"),
        ("auditoria", "0001_initial"),
        ("comercios", "0006_actividadcomercial_descripcion"),
        ("contenidos", "0005_alter_publicidad_foto"),
        ("cuotas", "0004_alter_cuota_estado"),
        ("gestion", "0004_agregar_permiso_auditoria"),
        ("usuarios", "0003_estadodatosstaging"),
    ]

    operations = [migrations.RunPython(configurar_grupos, migrations.RunPython.noop)]
