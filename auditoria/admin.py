from django.contrib import admin

from .models import EventoAuditoria


@admin.register(EventoAuditoria)
class EventoAuditoriaAdmin(admin.ModelAdmin):
    list_display = ("fecha", "actor_etiqueta", "accion", "entidad", "objeto_descripcion", "origen")
    list_filter = ("accion", "entidad", "origen", "fecha")
    search_fields = ("actor_etiqueta", "objeto_id", "objeto_descripcion")
    readonly_fields = (
        "fecha",
        "actor",
        "actor_etiqueta",
        "accion",
        "entidad",
        "objeto_id",
        "objeto_descripcion",
        "cambios",
        "motivo",
        "origen",
        "operacion_id",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
