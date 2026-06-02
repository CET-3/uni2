from django.urls import path

from .views import (
    GestionAsociadoDetalleView,
    GestionAsociadosView,
    GestionCobrosView,
    GestionDashboardView,
    GestionDeudoresView,
    GestionPeriodosCuotaView,
)


app_name = "gestion"

urlpatterns = [
    path("gestion/", GestionDashboardView.as_view(), name="dashboard"),
    path("gestion/asociados/", GestionAsociadosView.as_view(), name="asociados"),
    path("gestion/asociados/<int:asociado_id>/", GestionAsociadoDetalleView.as_view(), name="asociado_detalle"),
    path("gestion/deudores/", GestionDeudoresView.as_view(), name="deudores"),
    path("gestion/cobros/", GestionCobrosView.as_view(), name="cobros"),
    path("gestion/cuotas/periodos/", GestionPeriodosCuotaView.as_view(), name="periodos_cuota"),
]

