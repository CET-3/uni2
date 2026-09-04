"""Nombres y permisos de los roles iniciales de Uni2.

Los grupos son acumulables: una persona puede participar de más de un área.
Los permisos se expresan como ``app_label.codename`` para que la matriz sea
fácil de leer y reutilizar desde la carga inicial.
"""

ATENCION_ASOCIADO_GROUP = "Atención al asociado"
ADMINISTRADOR_PERMISOS_GROUP = "Administrador de permisos"
GESTION_CONVENIOS_GROUP = "Gestión de convenios"
GESTION_PRODUCTOS_SERVICIOS_GROUP = "Gestión de productos y servicios"
GESTION_PUBLICIDADES_GROUP = "Gestión de publicidades"
EQUIPO_PROYECTO_GROUP = "Equipo del proyecto"
ADMINISTRADOR_MUTUAL_GROUP = "Administrador de la mutual"
ADMINISTRADOR_APP_GROUP = "Administrador de la app"
ASOCIADO_GROUP = "Asociados"
COMERCIO_GROUP = "Comercios"
ACCESO_ADMIN_TECNICO = "usuarios.acceder_admin_tecnico"

GRUPOS_OPERATIVOS = (
    ATENCION_ASOCIADO_GROUP,
    ADMINISTRADOR_PERMISOS_GROUP,
    GESTION_CONVENIOS_GROUP,
    GESTION_PRODUCTOS_SERVICIOS_GROUP,
    GESTION_PUBLICIDADES_GROUP,
    EQUIPO_PROYECTO_GROUP,
    ADMINISTRADOR_MUTUAL_GROUP,
    ADMINISTRADOR_APP_GROUP,
)

DEFAULT_GROUPS = GRUPOS_OPERATIVOS + (ASOCIADO_GROUP, COMERCIO_GROUP)

PERMISOS_POR_GRUPO = {
    ATENCION_ASOCIADO_GROUP: (
        "gestion.consultar_asociados",
        "gestion.editar_asociados",
        "gestion.cobrar_cuotas",
        "gestion.ver_movimientos_asociado",
        "gestion.consultar_solicitudes_asociacion",
        "gestion.revisar_solicitudes_asociacion",
        "gestion.completar_solicitudes_asociacion",
        "gestion.cancelar_solicitudes_asociacion",
        "gestion.reenviar_comunicaciones",
    ),
    ADMINISTRADOR_PERMISOS_GROUP: (
        ACCESO_ADMIN_TECNICO,
        "gestion.ver_auditoria",
        "auth.view_user",
        "auth.add_user",
        "auth.change_user",
        "auth.view_group",
        "auditoria.view_eventoauditoria",
    ),
    GESTION_CONVENIOS_GROUP: (
        ACCESO_ADMIN_TECNICO,
        "comercios.view_actividadcomercial",
        "comercios.add_actividadcomercial",
        "comercios.change_actividadcomercial",
        "comercios.view_comercio",
        "comercios.add_comercio",
        "comercios.change_comercio",
    ),
    GESTION_PRODUCTOS_SERVICIOS_GROUP: (
        ACCESO_ADMIN_TECNICO,
        "contenidos.view_categoriaproductoservicio",
        "contenidos.add_categoriaproductoservicio",
        "contenidos.change_categoriaproductoservicio",
        "contenidos.view_productoservicio",
        "contenidos.add_productoservicio",
        "contenidos.change_productoservicio",
    ),
    GESTION_PUBLICIDADES_GROUP: (
        ACCESO_ADMIN_TECNICO,
        "contenidos.view_productoservicio",
        "contenidos.view_publicidad",
        "contenidos.add_publicidad",
        "contenidos.change_publicidad",
        "comercios.view_comercio",
    ),
    EQUIPO_PROYECTO_GROUP: (
        "gestion.ver_especificacion",
        "gestion.ver_design_system",
    ),
    ADMINISTRADOR_MUTUAL_GROUP: (
        ACCESO_ADMIN_TECNICO,
        "gestion.consultar_asociados",
        "gestion.editar_asociados",
        "gestion.exportar_asociados",
        "gestion.cobrar_cuotas",
        "gestion.ver_deudores",
        "gestion.administrar_periodos_cuota",
        "gestion.ver_auditoria",
        "gestion.ver_movimientos_asociado",
        "gestion.consultar_solicitudes_asociacion",
        "gestion.revisar_solicitudes_asociacion",
        "gestion.completar_solicitudes_asociacion",
        "gestion.cancelar_solicitudes_asociacion",
        "gestion.reenviar_comunicaciones",
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
    # Estos grupos describen una identidad o una responsabilidad técnica. No
    # otorgan permisos por sí solos.
    ADMINISTRADOR_APP_GROUP: (),
    ASOCIADO_GROUP: (),
    COMERCIO_GROUP: (),
}
