from django.urls import path

from .views import AsociadoCredencialView, AsociadoCuotasView, AsociadoDashboardView


app_name = "asociados"

urlpatterns = [
    path("panel/", AsociadoDashboardView.as_view(), name="dashboard"),
    path("credencial/", AsociadoCredencialView.as_view(), name="credencial"),
    path("cuotas/", AsociadoCuotasView.as_view(), name="cuotas"),
]

