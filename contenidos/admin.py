from django.contrib import admin

from .models import Beneficio, HorarioAtencion


@admin.register(Beneficio)
class BeneficioAdmin(admin.ModelAdmin):
    list_display = ("titulo", "activo", "orden")
    list_filter = ("activo",)


@admin.register(HorarioAtencion)
class HorarioAtencionAdmin(admin.ModelAdmin):
    list_display = ("dia_semana", "hora_desde", "hora_hasta", "activo")
    list_filter = ("activo", "dia_semana")
