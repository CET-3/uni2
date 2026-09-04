GESTION_CONSULTAR_ASOCIADOS = "gestion.consultar_asociados"
GESTION_EDITAR_ASOCIADOS = "gestion.editar_asociados"
GESTION_IMPORTAR_ASOCIADOS = "gestion.importar_asociados"
GESTION_EXPORTAR_ASOCIADOS = "gestion.exportar_asociados"
GESTION_COBRAR_CUOTAS = "gestion.cobrar_cuotas"
GESTION_VER_DEUDORES = "gestion.ver_deudores"
GESTION_ADMINISTRAR_PERIODOS_CUOTA = "gestion.administrar_periodos_cuota"
GESTION_IMPORTAR_CUOTAS_HISTORICAS = "gestion.importar_cuotas_historicas"
GESTION_VER_ESPECIFICACION = "gestion.ver_especificacion"
GESTION_VER_DESIGN_SYSTEM = "gestion.ver_design_system"
GESTION_VER_AUDITORIA = "gestion.ver_auditoria"
GESTION_VER_MOVIMIENTOS_ASOCIADO = "gestion.ver_movimientos_asociado"
GESTION_CONSULTAR_SOLICITUDES_ASOCIACION = "gestion.consultar_solicitudes_asociacion"
GESTION_REVISAR_SOLICITUDES_ASOCIACION = "gestion.revisar_solicitudes_asociacion"
GESTION_COMPLETAR_SOLICITUDES_ASOCIACION = "gestion.completar_solicitudes_asociacion"
GESTION_CANCELAR_SOLICITUDES_ASOCIACION = "gestion.cancelar_solicitudes_asociacion"
GESTION_REENVIAR_COMUNICACIONES = "gestion.reenviar_comunicaciones"


GESTION_PERMISSION_LABELS = [
    (GESTION_CONSULTAR_ASOCIADOS, "Puede consultar asociados"),
    (GESTION_EDITAR_ASOCIADOS, "Puede editar asociados"),
    (GESTION_IMPORTAR_ASOCIADOS, "Puede importar asociados"),
    (GESTION_EXPORTAR_ASOCIADOS, "Puede exportar asociados"),
    (GESTION_COBRAR_CUOTAS, "Puede cobrar cuotas"),
    (GESTION_VER_DEUDORES, "Puede ver deudores"),
    (GESTION_ADMINISTRAR_PERIODOS_CUOTA, "Puede administrar períodos de cuota"),
    (GESTION_IMPORTAR_CUOTAS_HISTORICAS, "Puede importar cuotas históricas"),
    (GESTION_VER_ESPECIFICACION, "Puede ver la especificación del proyecto"),
    (GESTION_VER_DESIGN_SYSTEM, "Puede ver el design system del proyecto"),
    (GESTION_VER_AUDITORIA, "Puede ver la auditoría de gestión"),
    (GESTION_VER_MOVIMIENTOS_ASOCIADO, "Puede ver los movimientos de la ficha del asociado"),
    (GESTION_CONSULTAR_SOLICITUDES_ASOCIACION, "Puede consultar solicitudes de asociación"),
    (GESTION_REVISAR_SOLICITUDES_ASOCIACION, "Puede revisar solicitudes de asociación"),
    (GESTION_COMPLETAR_SOLICITUDES_ASOCIACION, "Puede completar solicitudes de asociación"),
    (GESTION_CANCELAR_SOLICITUDES_ASOCIACION, "Puede cancelar solicitudes de asociación"),
    (GESTION_REENVIAR_COMUNICACIONES, "Puede reenviar comunicaciones"),
]

GESTION_PERMISSIONS = tuple(permission for permission, label in GESTION_PERMISSION_LABELS)


def user_has_gestion_permission(user, permission: str) -> bool:
    return bool(user.is_authenticated and user.has_perm(permission))


def user_has_any_gestion_permission(user) -> bool:
    return bool(user.is_authenticated and any(user.has_perm(permission) for permission in GESTION_PERMISSIONS))
