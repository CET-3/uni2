from django.urls import path

from .views import ComercioDashboardView, ValidarCredencialView


app_name = "comercios"

urlpatterns = [
    path("panel/", ComercioDashboardView.as_view(), name="dashboard"),
    path("validar-credencial/", ValidarCredencialView.as_view(), name="validar_credencial"),
]

