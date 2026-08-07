from django.urls import path

from . import views


app_name = "pwa"

urlpatterns = [
    path("manifest.webmanifest", views.manifest, name="manifest"),
    path("service-worker.js", views.service_worker, name="service_worker"),
    path("sin-conexion/", views.offline, name="offline"),
    path("sin-conexion/accion-no-enviada/", views.offline_action, name="offline_action"),
    path("sin-conexion/credencial/", views.offline_credential, name="offline_credential"),
]
