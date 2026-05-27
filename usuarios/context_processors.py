from .services import user_is_asociado, user_is_comercio


def navigation_roles(request):
    user = request.user
    es_asociado = user_is_asociado(user)
    es_comercio = user_is_comercio(user)
    tiene_perfil_asociado = bool(user.is_authenticated and hasattr(user, "asociado"))
    tiene_perfil_comercio = bool(user.is_authenticated and hasattr(user, "comercio"))
    return {
        "es_asociado": es_asociado,
        "es_comercio": es_comercio,
        "es_staff": bool(user.is_authenticated and user.is_staff),
        "tiene_perfil_asociado": tiene_perfil_asociado,
        "tiene_perfil_comercio": tiene_perfil_comercio,
    }
