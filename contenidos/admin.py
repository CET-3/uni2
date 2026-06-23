from django.contrib import admin

from .models import CategoriaProductoServicio, ProductoServicio


class ProductoServicioInline(admin.TabularInline):
    model = ProductoServicio
    extra = 0
    fields = ("nombre", "es_servicio", "precio_asociados", "precio_no_asociados", "activo", "orden")


@admin.register(CategoriaProductoServicio)
class CategoriaProductoServicioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activa", "orden")
    list_filter = ("activa",)
    search_fields = ("nombre", "descripcion", "texto_cta")
    inlines = [ProductoServicioInline]


@admin.register(ProductoServicio)
class ProductoServicioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "es_servicio", "precio_asociados", "precio_no_asociados", "activo", "orden")
    list_filter = ("activo", "es_servicio", "categoria")
    search_fields = ("nombre", "descripcion", "categoria__nombre")
    list_select_related = ("categoria",)
