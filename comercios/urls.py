from django.urls import path

from .views import MiConvenioView, ValidarCredencialView


app_name = "comercios"

urlpatterns = [
    path("validar-credencial/", ValidarCredencialView.as_view(), name="validar_credencial"),
    path("mi-convenio/", MiConvenioView.as_view(), name="mi_convenio"),
]
