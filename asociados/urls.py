from django.urls import path

from .views import (
    AsociadoCredencialView,
    AsociadoCuotasView,
    AsociadoDatosPropiosView,
)


app_name = "asociados"

urlpatterns = [
    path("credencial/", AsociadoCredencialView.as_view(), name="credencial"),
    path("cuotas/", AsociadoCuotasView.as_view(), name="cuotas"),
    path("mis-datos/", AsociadoDatosPropiosView.as_view(), name="datos_propios"),
]
