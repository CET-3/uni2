from django.contrib import admin

from auditoria.admin_mixins import AuditoriaAdminMixin
from config.formatting import formatear_moneda

from .models import Cuota, Donacion, Pago, PagoCuota, PeriodoCuota


class RegistroFinancieroSoloLecturaAdmin:
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PeriodoCuota)
class PeriodoCuotaAdmin(AuditoriaAdminMixin, admin.ModelAdmin):
    allow_superuser_delete = True
    audit_fields = (
        "mes",
        "ciclo_lectivo",
        "importe",
        "importe_recargo_mes",
        "importe_recargo_mes_siguiente",
        "fecha_vencimiento",
        "activo",
    )
    list_display = ("mes", "ciclo_lectivo", "importe_formateado", "fecha_vencimiento", "activo")
    list_filter = ("ciclo_lectivo", "activo")

    @admin.display(description="Importe", ordering="importe")
    def importe_formateado(self, obj):
        return formatear_moneda(obj.importe)


@admin.register(Cuota)
class CuotaAdmin(RegistroFinancieroSoloLecturaAdmin, admin.ModelAdmin):
    list_display = (
        "asociado",
        "periodo",
        "importe_formateado",
        "importe_pagado_formateado",
        "estado",
        "fecha_generacion",
    )
    list_filter = ("estado", "periodo__ciclo_lectivo")
    search_fields = ("asociado__apellido", "asociado__dni")

    @admin.display(description="Importe", ordering="importe")
    def importe_formateado(self, obj):
        return formatear_moneda(obj.importe)

    @admin.display(description="Importe pagado", ordering="importe_pagado")
    def importe_pagado_formateado(self, obj):
        return formatear_moneda(obj.importe_pagado)


class PagoCuotaInline(admin.TabularInline):
    model = PagoCuota
    extra = 0
    can_delete = False
    fields = ("cuota", "importe_formateado")
    readonly_fields = ("cuota", "importe_formateado")

    @admin.display(description="Importe")
    def importe_formateado(self, obj):
        return formatear_moneda(obj.importe)

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Pago)
class PagoAdmin(RegistroFinancieroSoloLecturaAdmin, admin.ModelAdmin):
    list_display = ("id", "asociado", "fecha", "importe_formateado", "metodo", "registrado_por")
    list_filter = ("metodo", "fecha")
    search_fields = ("asociado__apellido", "asociado__dni")
    inlines = [PagoCuotaInline]

    @admin.display(description="Importe", ordering="importe")
    def importe_formateado(self, obj):
        return formatear_moneda(obj.importe)


@admin.register(PagoCuota)
class PagoCuotaAdmin(RegistroFinancieroSoloLecturaAdmin, admin.ModelAdmin):
    list_display = ("pago", "cuota", "importe_formateado")

    @admin.display(description="Importe", ordering="importe")
    def importe_formateado(self, obj):
        return formatear_moneda(obj.importe)


@admin.register(Donacion)
class DonacionAdmin(RegistroFinancieroSoloLecturaAdmin, admin.ModelAdmin):
    list_display = ("asociado", "importe_formateado", "fecha", "pago")
    list_filter = ("fecha",)
    search_fields = ("asociado__apellido", "asociado__dni")

    @admin.display(description="Importe", ordering="importe")
    def importe_formateado(self, obj):
        return formatear_moneda(obj.importe)
