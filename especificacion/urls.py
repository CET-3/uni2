from django.urls import path

from .views import ArchivoView, IndiceView

app_name = "especificacion"

urlpatterns = [
    path("", IndiceView.as_view(), name="indice"),
    path("<path:ruta>/", ArchivoView.as_view(), name="archivo"),
]
