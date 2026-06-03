from django.contrib import admin

from .models import ActividadComercial, Comercio


@admin.register(ActividadComercial)
class ActividadComercialAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(Comercio)
class ComercioAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "actividad_comercial",
        "nombre",
        "beneficio_texto",
        "estado",
        "flyer_disponible",
        "direccion",
        "usuario",
        "propietario",
        "fecha_convenio",
        "notas",
        "email",
        "telefono",
        "url_presencia_web",
        "ciudad",
        "provincia",
        "latitud",
        "longitud",
    )
    autocomplete_fields = ("usuario",)
    list_select_related = ("actividad_comercial", "usuario")
    list_filter = ("estado", "actividad_comercial")
    search_fields = ("nombre", "propietario", "beneficio_texto", "url_presencia_web")
