from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordResetConfirmView,
)
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView

from comercios.services import validar_credencial

from .forms import (
    RecuperarContrasenaForm,
    Uni2AuthenticationForm,
    Uni2PasswordChangeForm,
    Uni2SetPasswordForm,
)
from .mixins import AsociadoRequiredMixin, CredentialPrivacyHeadersMixin
from .services import (
    solicitar_recuperacion_contrasena,
    user_is_asociado,
    user_is_comercio,
)


class Uni2LoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = Uni2AuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        if user_is_asociado(user) and not hasattr(user, "asociado"):
            messages.warning(
                self.request,
                "Tu usuario pertenece al rol de asociados, pero todavia no tiene un asociado vinculado.",
            )
        if user_is_comercio(user) and not hasattr(user, "comercio"):
            messages.warning(
                self.request,
                "Tu usuario pertenece al rol de comercios, pero todavia no tiene un comercio vinculado.",
            )
        return response

    def get_success_url(self):
        # LoginView valida que ``next`` sea una URL segura del mismo host.
        return self.get_redirect_url() or reverse_lazy("web:home")


class Uni2LogoutView(LogoutView):
    next_page = reverse_lazy("web:home")


class Uni2PasswordChangeView(AsociadoRequiredMixin, PasswordChangeView):
    template_name = "registration/password_change_form.html"
    form_class = Uni2PasswordChangeForm
    success_url = reverse_lazy("usuarios:cambiar_contrasena_lista")


class Uni2PasswordChangeDoneView(AsociadoRequiredMixin, TemplateView):
    template_name = "registration/password_change_done.html"


class RecuperarContrasenaView(CredentialPrivacyHeadersMixin, FormView):
    template_name = "registration/password_reset_form.html"
    form_class = RecuperarContrasenaForm
    success_url = reverse_lazy("usuarios:recuperacion_solicitada")

    def form_valid(self, form):
        solicitar_recuperacion_contrasena(**form.cleaned_data)
        return super().form_valid(form)


class RecuperacionSolicitadaView(
    CredentialPrivacyHeadersMixin, TemplateView
):
    template_name = "registration/password_reset_done.html"


class RestablecerContrasenaView(
    CredentialPrivacyHeadersMixin, PasswordResetConfirmView
):
    template_name = "registration/password_reset_confirm.html"
    form_class = Uni2SetPasswordForm
    success_url = reverse_lazy("usuarios:recuperacion_completada")


class RecuperacionCompletadaView(
    CredentialPrivacyHeadersMixin, TemplateView
):
    template_name = "registration/password_reset_complete.html"


class ResolverCredencialView(CredentialPrivacyHeadersMixin, LoginRequiredMixin, View):
    """Deriva la URL del QR a la experiencia habilitada para la sesión."""

    login_url = "usuarios:login"

    def get(self, request, token):
        asociado = getattr(request.user, "asociado", None)
        if asociado is not None and asociado.token_credencial == token:
            return redirect("asociados:credencial")

        comercio = getattr(request.user, "comercio", None)
        if comercio is not None and user_is_comercio(request.user):
            try:
                resultado = validar_credencial(comercio=comercio, token=token)
            except ValueError as exc:
                return render(
                    request,
                    "usuarios/credencial_no_disponible.html",
                    {"mensaje": str(exc)},
                    status=403,
                )
            return render(
                request,
                "comercios/resultado_validacion.html",
                {"resultado": resultado, "comercio": comercio},
            )

        if asociado is not None and user_is_asociado(request.user):
            return render(
                request,
                "usuarios/credencial_no_disponible.html",
                {"mensaje": "No se puede acceder a esta credencial."},
                status=404,
            )

        return render(
            request,
            "usuarios/credencial_no_disponible.html",
            {"mensaje": "Tu usuario no tiene permiso para abrir esta credencial."},
            status=403,
        )
