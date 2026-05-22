from django.urls import path

from .views import Uni2LoginView, Uni2LogoutView


app_name = "usuarios"

urlpatterns = [
    path("login/", Uni2LoginView.as_view(), name="login"),
    path("logout/", Uni2LogoutView.as_view(), name="logout"),
]

