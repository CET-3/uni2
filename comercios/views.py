from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView

from .services import validar_credencial
from usuarios.services import user_is_comercio


class ComercioRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = "usuarios:login"

    def test_func(self):
        return user_is_comercio(self.request.user) and hasattr(self.request.user, "comercio")

    def handle_no_permission(self):
        if self.request.user.is_authenticated and user_is_comercio(self.request.user):
            messages.warning(
                self.request,
                "Tu usuario tiene rol de comercio, pero todavia no tiene un comercio vinculado.",
            )
            return redirect("contenidos:home")
        return super().handle_no_permission()


class ValidarCredencialForm(forms.Form):
    token = forms.UUIDField(label="Token de credencial")


class ComercioDashboardView(ComercioRequiredMixin, TemplateView):
    template_name = "comercios/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comercio = self.request.user.comercio
        context["comercio"] = comercio
        return context


class ValidarCredencialView(ComercioRequiredMixin, FormView):
    template_name = "comercios/validar_credencial.html"
    form_class = ValidarCredencialForm

    def form_valid(self, form):
        comercio = self.request.user.comercio
        try:
            resultado = validar_credencial(comercio=comercio, token=form.cleaned_data["token"])
        except ValueError as exc:
            messages.error(self.request, str(exc))
            return self.form_invalid(form)

        context = self.get_context_data(form=form, resultado=resultado, comercio=comercio)
        return render(self.request, "comercios/resultado_validacion.html", context)
