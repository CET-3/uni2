from django.contrib import admin

from .models import Cuota, Pago, PagoCuota, PeriodoCuota


@admin.register(PeriodoCuota)
class PeriodoCuotaAdmin(admin.ModelAdmin):
    list_display = ("mes", "ciclo_lectivo", "importe", "fecha_vencimiento", "activo")
    list_filter = ("ciclo_lectivo", "activo")


@admin.register(Cuota)
class CuotaAdmin(admin.ModelAdmin):
    list_display = ("asociado", "periodo", "importe", "importe_pagado", "estado", "fecha_generacion")
    list_filter = ("estado", "periodo__ciclo_lectivo")
    search_fields = ("asociado__apellido", "asociado__dni")


class PagoCuotaInline(admin.TabularInline):
    model = PagoCuota
    extra = 0


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("id", "asociado", "fecha", "importe", "metodo", "registrado_por")
    list_filter = ("metodo", "fecha")
    search_fields = ("asociado__apellido", "asociado__dni")
    inlines = [PagoCuotaInline]


@admin.register(PagoCuota)
class PagoCuotaAdmin(admin.ModelAdmin):
    list_display = ("pago", "cuota", "importe")

