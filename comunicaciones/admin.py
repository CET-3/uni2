from django.contrib import admin

from .models import Comunicacion, EntregaComunicacion


class SoloLecturaAdminMixin:
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Comunicacion)
class ComunicacionAdmin(SoloLecturaAdminMixin, admin.ModelAdmin):
    list_display = ("creado_en", "tipo", "alcance", "origen_entidad", "origen_id")
    list_filter = ("alcance", "tipo", "creado_en")
    search_fields = ("tipo", "clave_idempotencia", "origen_entidad", "origen_id")
    readonly_fields = (
        "tipo",
        "alcance",
        "clave_idempotencia",
        "origen_entidad",
        "origen_id",
        "creado_en",
        "creado_por",
    )


@admin.register(EntregaComunicacion)
class EntregaComunicacionAdmin(SoloLecturaAdminMixin, admin.ModelAdmin):
    list_display = ("creado_en", "canal", "destino", "estado", "intentos")
    list_filter = ("canal", "estado", "creado_en")
    search_fields = ("destino", "comunicacion__tipo", "comunicacion__clave_idempotencia")
    readonly_fields = (
        "comunicacion",
        "canal",
        "destino",
        "estado",
        "intentos",
        "ultimo_intento_en",
        "enviado_en",
        "proveedor_id",
        "ultimo_error",
        "creado_en",
    )
