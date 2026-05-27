from django.urls import path

from .views import (
    GestionAsociadoDetalleView,
    GestionAsociadosView,
    GestionCobrosView,
    GestionDashboardView,
    GestionDeudoresView,
    GestionPeriodosCuotaView,
    Uni2LoginView,
    Uni2LogoutView,
)


app_name = "usuarios"

urlpatterns = [
    path("gestion/", GestionDashboardView.as_view(), name="gestion_dashboard"),
    path("gestion/asociados/", GestionAsociadosView.as_view(), name="gestion_asociados"),
    path(
        "gestion/asociados/<int:asociado_id>/",
        GestionAsociadoDetalleView.as_view(),
        name="gestion_asociado_detalle",
    ),
    path("gestion/deudores/", GestionDeudoresView.as_view(), name="gestion_deudores"),
    path("gestion/cobros/", GestionCobrosView.as_view(), name="gestion_cobros"),
    path("gestion/cuotas/periodos/", GestionPeriodosCuotaView.as_view(), name="gestion_periodos_cuota"),
    path("login/", Uni2LoginView.as_view(), name="login"),
    path("logout/", Uni2LogoutView.as_view(), name="logout"),
]
