from django.urls import path

from .views import (
    ComerciosPublicosView,
    HomeView,
    ProductosServiciosPublicosView,
)


app_name = "web"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("productos-servicios/", ProductosServiciosPublicosView.as_view(), name="productos_servicios"),
    path("comercios/", ComerciosPublicosView.as_view(), name="comercios"),
]
