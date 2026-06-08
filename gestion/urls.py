from django.urls import path

from .views import (
    GestionAsociadoDetalleView,
    GestionAsociadosView,
    GestionCobrosView,
    GestionDashboardView,
    GestionDeudoresView,
    GestionDescargarAsociadosRevisarView,
    GestionExportarAsociadosView,
    GestionImportarAsociadosView,
    GestionPeriodosCuotaView,
)


app_name = "gestion"

urlpatterns = [
    path("gestion/", GestionDashboardView.as_view(), name="dashboard"),
    path("gestion/asociados/", GestionAsociadosView.as_view(), name="asociados"),
    path("gestion/asociados/exportar.xlsx", GestionExportarAsociadosView.as_view(), name="exportar_asociados"),
    path("gestion/asociados/importar/", GestionImportarAsociadosView.as_view(), name="importar_asociados"),
    path(
        "gestion/asociados/importar/revisar.xlsx",
        GestionDescargarAsociadosRevisarView.as_view(),
        name="descargar_asociados_revisar",
    ),
    path("gestion/asociados/<int:asociado_id>/", GestionAsociadoDetalleView.as_view(), name="asociado_detalle"),
    path("gestion/deudores/", GestionDeudoresView.as_view(), name="deudores"),
    path("gestion/cobros/", GestionCobrosView.as_view(), name="cobros"),
    path("gestion/cuotas/periodos/", GestionPeriodosCuotaView.as_view(), name="periodos_cuota"),
]
