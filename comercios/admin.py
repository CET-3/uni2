from django.contrib import admin

from .models import ActividadComercial, Comercio


@admin.register(ActividadComercial)
class ActividadComercialAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")
    list_display_links = ("nombre",)
    fields = ("nombre", "descripcion")
    search_fields = ("nombre", "descripcion")


@admin.register(Comercio)
class ComercioAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "descripcion",
        "actividad_comercial",
        "beneficio_texto",
        "estado",
        "orden",
        "direccion",
        "usuario",
        "propietario",
        "fecha_convenio",
        "email",
        "telefono",
        "url_presencia_web",
        "ciudad",
        "provincia",
        "latitud",
        "longitud",
        "id",
    )
    list_display_links = ("nombre",)
    fields = (
        "actividad_comercial",
        "nombre",
        "descripcion",
        "beneficio_texto",
        "estado",
        "orden",
        "foto",
        "direccion",
        "url_presencia_web",
        "telefono",
        "email",
        "propietario",
        "fecha_convenio",
        "ciudad",
        "provincia",
        "latitud",
        "longitud",
        "usuario",
    )
    autocomplete_fields = ("usuario",)
    list_select_related = ("actividad_comercial", "usuario")
    list_filter = ("estado", "actividad_comercial")
    search_fields = (
        "nombre",
        "descripcion",
        "propietario",
        "beneficio_texto",
        "url_presencia_web",
    )
