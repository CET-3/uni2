from django.db import migrations
from django.db.models import Q

ACCESO_ADMIN = "usuarios.acceder_admin_tecnico"
PUBLICIDADES = "Gestión de publicidades"
PRODUCTOS = "Gestión de productos y servicios"
EQUIPO = "Equipo del proyecto"

PERMISOS_POR_GRUPO = {
    "Atención al asociado": (
        "gestion.ver_dashboard_gestion",
        "gestion.consultar_asociados",
        "gestion.editar_asociados",
        "gestion.cobrar_cuotas",
        "gestion.ver_movimientos_asociado",
    ),
    "Administrador de permisos": (
        ACCESO_ADMIN,
        "gestion.ver_dashboard_gestion",
        "gestion.ver_auditoria",
        "auth.view_user",
        "auth.add_user",
        "auth.change_user",
        "auth.view_group",
        "auditoria.view_eventoauditoria",
    ),
    "Gestión de convenios": (
        ACCESO_ADMIN,
        "gestion.ver_dashboard_gestion",
        "comercios.view_actividadcomercial",
        "comercios.add_actividadcomercial",
        "comercios.change_actividadcomercial",
        "comercios.view_comercio",
        "comercios.add_comercio",
        "comercios.change_comercio",
    ),
    PRODUCTOS: (
        ACCESO_ADMIN,
        "gestion.ver_dashboard_gestion",
        "contenidos.view_categoriaproductoservicio",
        "contenidos.add_categoriaproductoservicio",
        "contenidos.change_categoriaproductoservicio",
        "contenidos.view_productoservicio",
        "contenidos.add_productoservicio",
        "contenidos.change_productoservicio",
    ),
    PUBLICIDADES: (
        ACCESO_ADMIN,
        "gestion.ver_dashboard_gestion",
        "contenidos.view_productoservicio",
        "contenidos.view_publicidad",
        "contenidos.add_publicidad",
        "contenidos.change_publicidad",
        "comercios.view_comercio",
    ),
    EQUIPO: (
        "gestion.ver_dashboard_gestion",
        "gestion.ver_especificacion",
        "gestion.ver_design_system",
    ),
    "Administrador de la mutual": (
        ACCESO_ADMIN,
        "gestion.ver_dashboard_gestion",
        "gestion.consultar_asociados",
        "gestion.editar_asociados",
        "gestion.exportar_asociados",
        "gestion.cobrar_cuotas",
        "gestion.ver_deudores",
        "gestion.administrar_periodos_cuota",
        "gestion.ver_auditoria",
        "gestion.ver_movimientos_asociado",
        "asociados.view_asociado",
        "asociados.add_asociado",
        "asociados.change_asociado",
        "asociados.view_ciclolectivo",
        "asociados.add_ciclolectivo",
        "asociados.change_ciclolectivo",
        "asociados.view_curso",
        "asociados.add_curso",
        "asociados.change_curso",
        "comercios.view_actividadcomercial",
        "comercios.add_actividadcomercial",
        "comercios.change_actividadcomercial",
        "comercios.view_comercio",
        "comercios.add_comercio",
        "comercios.change_comercio",
        "contenidos.view_categoriaproductoservicio",
        "contenidos.add_categoriaproductoservicio",
        "contenidos.change_categoriaproductoservicio",
        "contenidos.view_productoservicio",
        "contenidos.add_productoservicio",
        "contenidos.change_productoservicio",
        "contenidos.view_publicidad",
        "contenidos.add_publicidad",
        "contenidos.change_publicidad",
        "cuotas.view_periodocuota",
        "cuotas.add_periodocuota",
        "cuotas.change_periodocuota",
        "cuotas.view_cuota",
        "cuotas.view_pago",
        "cuotas.view_pagocuota",
        "cuotas.view_donacion",
        "auditoria.view_eventoauditoria",
        "auth.view_user",
    ),
    "Administrador de la app": (),
    "Asociados": (),
    "Comercios": (),
}


def reorganizar_grupos(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    User = apps.get_model("auth", "User")

    publicidad, _ = Group.objects.get_or_create(name=PUBLICIDADES)
    productos, _ = Group.objects.get_or_create(name=PRODUCTOS)

    # El grupo anterior administraba ambos dominios. Copiar sus integrantes al
    # grupo nuevo conserva el acceso hasta que se revisen los perfiles reales.
    for user in publicidad.user_set.all():
        user.groups.add(productos)

    available = {
        f"{permission.content_type.app_label}.{permission.codename}": permission
        for permission in Permission.objects.select_related("content_type")
    }
    for group_name, permission_names in PERMISOS_POR_GRUPO.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        group.permissions.set(available[name] for name in permission_names)

    admin_permission = available[ACCESO_ADMIN]
    should_be_staff = (
        Q(is_superuser=True)
        | Q(groups__permissions=admin_permission)
        | Q(user_permissions=admin_permission)
    )
    staff_ids = User.objects.filter(should_be_staff).values("pk")
    User.objects.filter(pk__in=staff_ids).update(is_staff=True)
    User.objects.filter(is_staff=True, is_superuser=False).exclude(
        pk__in=staff_ids
    ).update(is_staff=False)


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0005_capacidad_acceso_admin"),
        ("gestion", "0005_agregar_permiso_movimientos_asociado"),
    ]

    operations = [
        migrations.RunPython(reorganizar_grupos, migrations.RunPython.noop),
    ]
