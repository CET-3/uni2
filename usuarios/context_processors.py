from .roles import ACCESO_ADMIN_TECNICO
from .services import get_available_experiences, user_has_gestion_access, user_is_asociado, user_is_comercio


def navigation_roles(request):
    user = request.user
    es_asociado = user_is_asociado(user)
    es_comercio = user_is_comercio(user)
    tiene_perfil_asociado = bool(user.is_authenticated and hasattr(user, "asociado"))
    tiene_perfil_comercio = bool(user.is_authenticated and hasattr(user, "comercio"))
    experiencias_disponibles = get_available_experiences(user)
    nombre_usuario = user.get_full_name() or user.get_username() if user.is_authenticated else ""
    return {
        "es_asociado": es_asociado,
        "es_comercio": es_comercio,
        "tiene_gestion": user_has_gestion_access(user),
        "tiene_admin_tecnico": bool(
            user.is_authenticated and user.has_perm(ACCESO_ADMIN_TECNICO)
        ),
        "tiene_perfil_asociado": tiene_perfil_asociado,
        "tiene_perfil_comercio": tiene_perfil_comercio,
        "experiencias_disponibles": experiencias_disponibles,
        "cantidad_experiencias": len(experiencias_disponibles),
        "nombre_usuario": nombre_usuario,
    }
