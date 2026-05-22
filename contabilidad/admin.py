from django.contrib import admin

from .models import Asiento, CuentaContable, PartidaAsiento


@admin.register(CuentaContable)
class CuentaContableAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "tipo", "activa")
    list_filter = ("tipo", "activa")
    search_fields = ("codigo", "nombre")


class PartidaAsientoInline(admin.TabularInline):
    model = PartidaAsiento
    extra = 0


@admin.register(Asiento)
class AsientoAdmin(admin.ModelAdmin):
    list_display = ("fecha", "descripcion", "tipo", "importe", "origen")
    list_filter = ("tipo", "fecha")
    search_fields = ("descripcion",)
    inlines = [PartidaAsientoInline]


@admin.register(PartidaAsiento)
class PartidaAsientoAdmin(admin.ModelAdmin):
    list_display = ("asiento", "cuenta", "movimiento", "importe")
    list_filter = ("movimiento", "cuenta__tipo")
    search_fields = ("asiento__descripcion", "cuenta__nombre", "cuenta__codigo")
