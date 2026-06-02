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
        "estado",
        "beneficio_texto",
        *tuple(
            field.name
            for field in Comercio._meta.fields
            if field.name not in {"nombre", "actividad_comercial", "estado", "beneficio_texto"}
        ),
    )
    list_filter = ("estado", "provincia", "actividad_comercial")
    search_fields = ("nombre", "propietario", "beneficio_texto", "url_presencia_web")
