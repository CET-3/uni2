from django.contrib import admin

from .models import Beneficio, HorarioAtencion, Publicidad, Servicio


@admin.register(Beneficio)
class BeneficioAdmin(admin.ModelAdmin):
    list_display = ("titulo", "activo", "orden")
    list_filter = ("activo",)


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio_referencia", "activo", "orden")
    list_filter = ("activo",)


@admin.register(Publicidad)
class PublicidadAdmin(admin.ModelAdmin):
    list_display = ("titulo", "activo", "fecha_desde", "fecha_hasta", "orden")
    list_filter = ("activo",)


@admin.register(HorarioAtencion)
class HorarioAtencionAdmin(admin.ModelAdmin):
    list_display = ("dia_semana", "hora_desde", "hora_hasta", "activo")
    list_filter = ("activo", "dia_semana")

