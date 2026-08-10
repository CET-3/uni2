from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

from .services import user_is_asociado, user_is_comercio


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
        return reverse_lazy("web:home")


class Uni2LogoutView(LogoutView):
    next_page = reverse_lazy("web:home")
