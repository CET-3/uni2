from django.urls import path

from .views import (
    RecuperacionCompletadaView,
    RecuperacionSolicitadaView,
    RecuperarContrasenaView,
    ResolverCredencialView,
    RestablecerContrasenaView,
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
    path(
        "recuperar-contrasena/",
        RecuperarContrasenaView.as_view(),
        name="recuperar_contrasena",
    ),
    path(
        "recuperar-contrasena/solicitada/",
        RecuperacionSolicitadaView.as_view(),
        name="recuperacion_solicitada",
    ),
    path(
        "recuperar-contrasena/<uidb64>/<token>/",
        RestablecerContrasenaView.as_view(),
        name="restablecer_contrasena",
    ),
    path(
        "recuperar-contrasena/completada/",
        RecuperacionCompletadaView.as_view(),
        name="recuperacion_completada",
    ),
    path("login/", Uni2LoginView.as_view(), name="login"),
    path("logout/", Uni2LogoutView.as_view(), name="logout"),
]
