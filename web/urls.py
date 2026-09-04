from django.urls import path

from .views import (
    ActividadComercialDetalleView,
    CategoriaProductoServicioDetalleView,
    ComercioDetalleView,
    ComercioDetalleModalView,
    ComerciosPublicosView,
    DesignSystemEstructuraView,
    DesignSystemView,
    HomeView,
    PreinscripcionCorreccionesRecibidasView,
    PreinscripcionRecibidaView,
    PreinscripcionView,
    ProductoServicioDetalleView,
    ProductosServiciosPublicosView,
    SolicitudSeguimientoView,
)


app_name = "web"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("sumate/", PreinscripcionView.as_view(), name="preinscripcion"),
    path(
        "sumate/recibida/",
        PreinscripcionRecibidaView.as_view(),
        name="preinscripcion_recibida",
    ),
    path(
        "sumate/correcciones-recibidas/",
        PreinscripcionCorreccionesRecibidasView.as_view(),
        name="preinscripcion_correcciones_recibidas",
    ),
    path(
        "sumate/solicitud/<str:token>/",
        SolicitudSeguimientoView.as_view(),
        name="solicitud_seguimiento",
    ),
    path("productos-servicios/", ProductosServiciosPublicosView.as_view(), name="productos_servicios"),
    path("productos-servicios/<int:pk>/", ProductoServicioDetalleView.as_view(), name="producto_servicio_detalle"),
    path("comercios/", ComerciosPublicosView.as_view(), name="comercios"),
    path(
        "comercios/<int:pk>/modal/",
        ComercioDetalleModalView.as_view(),
        name="comercio_detalle_modal",
    ),
    path("comercios/<int:pk>/", ComercioDetalleView.as_view(), name="comercio_detalle"),
    path("servicios/<int:pk>/", CategoriaProductoServicioDetalleView.as_view(), name="categoria_detalle"),
    path("actividades-comerciales/<int:pk>/", ActividadComercialDetalleView.as_view(), name="actividad_comercial_detalle"),
    path("design-system/", DesignSystemView.as_view(), name="design-system"),
    path("design-system/estructura/", DesignSystemEstructuraView.as_view(), name="design-system-estructura"),
]
