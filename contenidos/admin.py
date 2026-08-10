from django.contrib import admin

from auditoria.admin_mixins import AuditoriaAdminMixin
from config.formatting import formatear_moneda

from .models import CategoriaProductoServicio, ProductoServicio, Publicidad


class ProductoServicioInline(admin.TabularInline):
    model = ProductoServicio
    extra = 0
    fields = ("nombre", "es_servicio", "precio_asociados", "precio_no_asociados", "activo", "orden")
    can_delete = False


@admin.register(CategoriaProductoServicio)
class CategoriaProductoServicioAdmin(AuditoriaAdminMixin, admin.ModelAdmin):
    audit_fields = ("nombre", "descripcion", "etiqueta_icono", "texto_cta", "activa", "orden")
    audit_inline_fields = {
        ProductoServicio: (
            "categoria",
            "nombre",
            "descripcion",
            "es_servicio",
            "precio_asociados",
            "precio_no_asociados",
            "activo",
            "orden",
        )
    }
    list_display = ("nombre", "activa", "orden")
    list_filter = ("activa",)
    search_fields = ("nombre", "descripcion", "texto_cta")
    inlines = [ProductoServicioInline]


@admin.register(ProductoServicio)
class ProductoServicioAdmin(AuditoriaAdminMixin, admin.ModelAdmin):
    audit_fields = (
        "categoria",
        "nombre",
        "descripcion",
        "es_servicio",
        "precio_asociados",
        "precio_no_asociados",
        "activo",
        "orden",
    )
    list_display = (
        "nombre",
        "categoria",
        "es_servicio",
        "precio_asociados_formateado",
        "precio_no_asociados_formateado",
        "activo",
        "orden",
    )
    list_filter = ("activo", "es_servicio", "categoria")
    search_fields = ("nombre", "descripcion", "categoria__nombre")
    list_select_related = ("categoria",)

    @admin.display(description="Precio para asociados", ordering="precio_asociados")
    def precio_asociados_formateado(self, obj):
        return formatear_moneda(obj.precio_asociados)

    @admin.display(description="Precio para no asociados", ordering="precio_no_asociados")
    def precio_no_asociados_formateado(self, obj):
        return formatear_moneda(obj.precio_no_asociados)


@admin.register(Publicidad)
class PublicidadAdmin(AuditoriaAdminMixin, admin.ModelAdmin):
    audit_fields = (
        "titulo",
        "descripcion",
        "etiqueta_principal",
        "etiqueta_secundaria",
        "foto",
        "producto_servicio",
        "comercio",
        "activa",
        "orden",
    )
    list_display = ("titulo", "producto_servicio", "comercio", "etiqueta_principal", "activa", "orden")
    list_filter = ("activa", "etiqueta_principal")
    search_fields = ("titulo", "descripcion", "etiqueta_principal", "etiqueta_secundaria")
    list_select_related = ("producto_servicio", "comercio")
