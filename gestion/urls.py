from django.urls import path

from .views import (
    GestionAsociadoDetalleView,
    GestionAsociadoEditarView,
    GestionAsociadoCuotasView,
    GestionAsociadoNuevoView,
    GestionAsociadosView,
    GestionAuditoriaView,
    GestionCobrosView,
    GestionCrearUsuariosAsociadosFaltantesView,
    GestionCrearUsuarioAsociadoView,
    GestionDeudoresView,
    GestionDescargarAsociadosRevisarView,
    GestionDescargarCuotasHistoricasRevisarView,
    GestionExportarAsociadosView,
    GestionImportarAsociadosView,
    GestionImportarCuotasHistoricasView,
    GestionPeriodosCuotaView,
)


app_name = "gestion"

urlpatterns = [
    path("gestion/auditoria/", GestionAuditoriaView.as_view(), name="auditoria"),
    path("gestion/asociados/", GestionAsociadosView.as_view(), name="asociados"),
    path("gestion/asociados/nuevo/", GestionAsociadoNuevoView.as_view(), name="asociado_nuevo"),
    path("gestion/asociados/exportar.xlsx", GestionExportarAsociadosView.as_view(), name="exportar_asociados"),
    path("gestion/asociados/importar/", GestionImportarAsociadosView.as_view(), name="importar_asociados"),
    path(
        "gestion/asociados/crear-usuarios-faltantes/",
        GestionCrearUsuariosAsociadosFaltantesView.as_view(),
        name="crear_usuarios_asociados_faltantes",
    ),
    path(
        "gestion/asociados/importar/revisar.xlsx",
        GestionDescargarAsociadosRevisarView.as_view(),
        name="descargar_asociados_revisar",
    ),
    path("gestion/asociados/<int:asociado_id>/", GestionAsociadoDetalleView.as_view(), name="asociado_detalle"),
    path("gestion/asociados/<int:asociado_id>/cuotas/", GestionAsociadoCuotasView.as_view(), name="asociado_cuotas"),
    path("gestion/asociados/<int:asociado_id>/editar/", GestionAsociadoEditarView.as_view(), name="asociado_editar"),
    path("gestion/asociados/<int:asociado_id>/crear-usuario/", GestionCrearUsuarioAsociadoView.as_view(), name="crear_usuario_asociado"),
    path("gestion/deudores/", GestionDeudoresView.as_view(), name="deudores"),
    path("gestion/cobros/", GestionCobrosView.as_view(), name="cobros"),
    path("gestion/cuotas/importar-historicas/", GestionImportarCuotasHistoricasView.as_view(), name="importar_cuotas_historicas"),
    path(
        "gestion/cuotas/importar-historicas/revisar.xlsx",
        GestionDescargarCuotasHistoricasRevisarView.as_view(),
        name="descargar_cuotas_historicas_revisar",
    ),
    path("gestion/cuotas/periodos/", GestionPeriodosCuotaView.as_view(), name="periodos_cuota"),
]
