from django.urls import path

from .views import ResolverCredencialView, Uni2LoginView, Uni2LogoutView


app_name = "usuarios"

urlpatterns = [
    path("credenciales/<uuid:token>/", ResolverCredencialView.as_view(), name="resolver_credencial"),
    path("login/", Uni2LoginView.as_view(), name="login"),
    path("logout/", Uni2LogoutView.as_view(), name="logout"),
]
