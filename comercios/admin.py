from django.contrib import admin

from .models import ActividadComercial, Comercio


@admin.register(ActividadComercial)
class ActividadComercialAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(Comercio)
class ComercioAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "actividad_comercial",
        "propietario",
        "estado",
        "telefono",
        "ciudad",
    )
    list_filter = ("estado", "provincia", "actividad_comercial")
    search_fields = ("nombre", "propietario", "beneficio_texto", "url_presencia_web")
