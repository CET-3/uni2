from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect

from .services import user_is_asociado


class CredentialPrivacyHeadersMixin:
    """Evita que respuestas vinculadas a un token queden almacenadas o referidas."""

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        response.headers["Cache-Control"] = "private, no-store"
        response.headers["Referrer-Policy"] = "same-origin"
        return response


class AsociadoRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Restringe una vista a usuarios con rol y perfil de asociado."""

    login_url = "usuarios:login"

    def test_func(self):
        return user_is_asociado(self.request.user) and hasattr(
            self.request.user, "asociado"
        )

    def handle_no_permission(self):
        if self.request.user.is_authenticated and user_is_asociado(
            self.request.user
        ):
            messages.warning(
                self.request,
                "Tu usuario tiene rol de asociado, pero todavia no tiene un asociado vinculado.",
            )
            return redirect("web:home")
        return super().handle_no_permission()
