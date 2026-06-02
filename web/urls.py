from django.urls import path

from .views import (
    BeneficiosPublicosView,
    ComerciosPublicosView,
    HomeView,
    HorariosPublicosView,
)


app_name = "web"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("beneficios/", BeneficiosPublicosView.as_view(), name="beneficios"),
    path("horarios/", HorariosPublicosView.as_view(), name="horarios"),
    path("comercios/", ComerciosPublicosView.as_view(), name="comercios"),
]
