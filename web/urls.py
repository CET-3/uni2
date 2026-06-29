from django.urls import path

from .views import (
    ActividadComercialDetalleView,
    CategoriaProductoServicioDetalleView,
    ComercioDetalleView,
    ComerciosPublicosView,
    DesignSystemEstructuraView,
    DesignSystemView,
    PublicHomeView,
    SmartStartView,
    ProductoServicioDetalleView,
    ProductosServiciosPublicosView,
)


app_name = "web"

urlpatterns = [
    path("", SmartStartView.as_view(), name="home"),
    path("inicio/", PublicHomeView.as_view(), name="inicio"),
    path("productos-servicios/", ProductosServiciosPublicosView.as_view(), name="productos_servicios"),
    path("productos-servicios/<int:pk>/", ProductoServicioDetalleView.as_view(), name="producto_servicio_detalle"),
    path("comercios/", ComerciosPublicosView.as_view(), name="comercios"),
    path("comercios/<int:pk>/", ComercioDetalleView.as_view(), name="comercio_detalle"),
    path("servicios/<int:pk>/", CategoriaProductoServicioDetalleView.as_view(), name="categoria_detalle"),
    path("actividades-comerciales/<int:pk>/", ActividadComercialDetalleView.as_view(), name="actividad_comercial_detalle"),
    path("design-system/", DesignSystemView.as_view(), name="design-system"),
    path("design-system/estructura/", DesignSystemEstructuraView.as_view(), name="design-system-estructura"),
]
