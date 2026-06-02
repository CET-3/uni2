from django.urls import path

from .views import (
    BeneficiosPublicosView,
    ComerciosPublicosView,
    HomeView,
    HorariosPublicosView,
    ServiciosPublicosView,
)


app_name = "web"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("beneficios/", BeneficiosPublicosView.as_view(), name="beneficios"),
    path("servicios/", ServiciosPublicosView.as_view(), name="servicios"),
    path("horarios/", HorariosPublicosView.as_view(), name="horarios"),
    path("comercios/", ComerciosPublicosView.as_view(), name="comercios"),
]

