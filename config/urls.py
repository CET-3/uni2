from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("contenidos.urls")),
    path("", include("usuarios.urls")),
    path("asociado/", include("asociados.urls")),
    path("comercio/", include("comercios.urls")),
]
