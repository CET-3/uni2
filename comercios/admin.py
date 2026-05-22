from django.contrib import admin

from .models import BeneficioComercio, Comercio


class BeneficioComercioInline(admin.TabularInline):
    model = BeneficioComercio
    extra = 0


@admin.register(Comercio)
class ComercioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "responsable", "telefono", "url_presencia_web", "ciudad", "activo")
    list_filter = ("activo", "provincia")
    search_fields = ("nombre", "responsable", "url_presencia_web")
    inlines = [BeneficioComercioInline]


@admin.register(BeneficioComercio)
class BeneficioComercioAdmin(admin.ModelAdmin):
    list_display = ("titulo", "comercio", "tipo_descuento", "activo", "fecha_desde", "fecha_hasta")
    list_filter = ("activo", "tipo_descuento")
    search_fields = ("titulo", "comercio__nombre")
