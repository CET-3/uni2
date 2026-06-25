from django.urls import path

from .views import (
    ActividadComercialDetalleView,
    CategoriaProductoServicioDetalleView,
    ComercioDetalleView,
    ComerciosPublicosView,
    DesignSystemView,
    HomeView,
    ProductoServicioDetalleView,
    ProductosServiciosPublicosView,
)


app_name = "web"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("productos-servicios/", ProductosServiciosPublicosView.as_view(), name="productos_servicios"),
    path("productos-servicios/<int:pk>/", ProductoServicioDetalleView.as_view(), name="producto_servicio_detalle"),
    path("comercios/", ComerciosPublicosView.as_view(), name="comercios"),
    path("comercios/<int:pk>/", ComercioDetalleView.as_view(), name="comercio_detalle"),
    path("servicios/<int:pk>/", CategoriaProductoServicioDetalleView.as_view(), name="categoria_detalle"),
    path("actividades-comerciales/<int:pk>/", ActividadComercialDetalleView.as_view(), name="actividad_comercial_detalle"),
    path("design-system/", DesignSystemView.as_view(), name="design-system"),
]
