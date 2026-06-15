from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from .services import get_available_experiences, user_is_asociado, user_is_comercio


class Uni2LoginView(LoginView):
    template_name = "registration/login.html"
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
        experiences = get_available_experiences(self.request.user)
        if len(experiences) > 1:
            return reverse_lazy("usuarios:selector_panel")
        if experiences == ["gestion"]:
            return reverse_lazy("gestion:dashboard")
        if experiences == ["asociado"]:
            return reverse_lazy("asociados:dashboard")
        if experiences == ["comercio"]:
            return reverse_lazy("comercios:dashboard")
        return reverse_lazy("web:home")


class Uni2LogoutView(LogoutView):
    next_page = reverse_lazy("web:home")


class SelectorPanelView(LoginRequiredMixin, TemplateView):
    template_name = "usuarios/selector_panel.html"
    login_url = "usuarios:login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        experiences = get_available_experiences(self.request.user)
        context["mostrar_asociado"] = "asociado" in experiences
        context["mostrar_comercio"] = "comercio" in experiences
        context["mostrar_gestion"] = "gestion" in experiences
        return context
