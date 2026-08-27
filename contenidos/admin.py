from django.contrib import admin

from auditoria.admin_mixins import AuditoriaAdminMixin
from config.formatting import formatear_moneda

from .forms import ProductoServicioAdminForm
from .models import CategoriaProductoServicio, Novedad, ProductoServicio, Publicidad


class ProductoServicioInline(admin.TabularInline):
    model = ProductoServicio
    form = ProductoServicioAdminForm
    extra = 0
    fields = (
        "nombre",
        "foto",
        "es_servicio",
        "ciclo_destinatario",
        "curso_destinatario",
        "precio_asociados",
        "precio_no_asociados",
        "activo",
        "orden",
    )
    can_delete = False


@admin.register(CategoriaProductoServicio)
class CategoriaProductoServicioAdmin(AuditoriaAdminMixin, admin.ModelAdmin):
    audit_fields = (
        "nombre",
        "descripcion",
        "etiqueta_icono",
        "texto_cta",
        "imagen_informativa",
        "titulo_imagen_informativa",
        "activa",
        "orden",
    )
    audit_inline_fields = {
        ProductoServicio: (
            "categoria",
            "nombre",
            "descripcion",
            "foto",
            "es_servicio",
            "ciclo_destinatario",
            "curso_destinatario",
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
    form = ProductoServicioAdminForm
    audit_fields = (
        "categoria",
        "nombre",
        "descripcion",
        "foto",
        "es_servicio",
        "ciclo_destinatario",
        "curso_destinatario",
        "precio_asociados",
        "precio_no_asociados",
        "activo",
        "orden",
    )
    list_display = (
        "nombre",
        "categoria",
        "es_servicio",
        "ciclo_destinatario",
        "curso_destinatario",
        "precio_asociados_formateado",
        "precio_no_asociados_formateado",
        "activo",
        "orden",
    )
    list_filter = ("activo", "es_servicio", "ciclo_destinatario", "categoria")
    search_fields = ("nombre", "descripcion", "curso_destinatario", "categoria__nombre")
    list_select_related = ("categoria",)

    @admin.display(description="Precio para asociados", ordering="precio_asociados")
    def precio_asociados_formateado(self, obj):
        if obj.precio_asociados is None:
            return "—"
        return formatear_moneda(obj.precio_asociados)

    @admin.display(description="Precio para no asociados", ordering="precio_no_asociados")
    def precio_no_asociados_formateado(self, obj):
        if obj.precio_no_asociados is None:
            return "—"
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


@admin.register(Novedad)
class NovedadAdmin(AuditoriaAdminMixin, admin.ModelAdmin):
    audit_fields = (
        "titulo",
        "slug",
        "etiqueta",
        "resumen",
        "contenido",
        "imagen",
        "color",
        "fecha_publicacion",
        "destacada",
        "activa",
    )
    list_display = ("titulo", "etiqueta", "fecha_publicacion", "color", "destacada", "activa")
    list_filter = ("activa", "destacada", "color", "fecha_publicacion")
    search_fields = ("titulo", "etiqueta", "resumen", "contenido")
    prepopulated_fields = {"slug": ("titulo",)}
