from types import SimpleNamespace

from django.contrib.admin import AdminSite


def user_can_access_admin(user, site, request=None):
    """Devuelve si el usuario tiene alguna capacidad sobre un modelo del admin."""
    if not user.is_authenticated or not user.is_active:
        return False
    if user.is_superuser:
        return True

    request = request or SimpleNamespace(user=user)
    return any(
        any(model_admin.get_model_perms(request).values())
        for model_admin in site._registry.values()
    )


class Uni2AdminSite(AdminSite):
    def has_permission(self, request):
        return user_can_access_admin(request.user, self, request=request)
