from django.urls import path

from .views import (
    ResolverCredencialView,
    Uni2LoginView,
    Uni2LogoutView,
    Uni2PasswordChangeDoneView,
    Uni2PasswordChangeView,
)


app_name = "usuarios"

urlpatterns = [
    path("credenciales/<uuid:token>/", ResolverCredencialView.as_view(), name="resolver_credencial"),
    path(
        "cambiar-contrasena/",
        Uni2PasswordChangeView.as_view(),
        name="cambiar_contrasena",
    ),
    path(
        "cambiar-contrasena/lista/",
        Uni2PasswordChangeDoneView.as_view(),
        name="cambiar_contrasena_lista",
    ),
    path("login/", Uni2LoginView.as_view(), name="login"),
    path("logout/", Uni2LogoutView.as_view(), name="logout"),
]
