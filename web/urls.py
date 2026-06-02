from django.urls import path

from .views import (
    BeneficiosPublicosView,
    ComerciosPublicosView,
    HomeView,
)


app_name = "web"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("beneficios/", BeneficiosPublicosView.as_view(), name="beneficios"),
    path("comercios/", ComerciosPublicosView.as_view(), name="comercios"),
]
