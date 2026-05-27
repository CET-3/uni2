import os

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def debug_files(request):
    base = "/var/task"
    result = {}
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in ("_vendor", "__pycache__", ".git")]
        rel = os.path.relpath(root, base)
        result[rel] = files
    return JsonResponse(result)


urlpatterns = [
    path("__debug__/", debug_files),
    path("admin/", admin.site.urls),
    path("", include("contenidos.urls")),
    path("", include(("usuarios.urls", "usuarios"), namespace="usuarios")),
    path("asociado/", include(("asociados.urls", "asociados"), namespace="asociados")),
    path("comercio/", include(("comercios.urls", "comercios"), namespace="comercios")),
]
