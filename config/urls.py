from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("contenidos.urls")),
    path("", include(("usuarios.urls", "usuarios"), namespace="usuarios")),
    path("asociado/", include(("asociados.urls", "asociados"), namespace="asociados")),
    path("comercio/", include(("comercios.urls", "comercios"), namespace="comercios")),
]
