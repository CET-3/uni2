from django.urls import path

from .views import ValidarCredencialView


app_name = "comercios"

urlpatterns = [
    path("validar-credencial/", ValidarCredencialView.as_view(), name="validar_credencial"),
]
