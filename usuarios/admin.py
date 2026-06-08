from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Notificacion


admin.site.unregister(User)


@admin.register(User)
class Uni2UserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "mostrar_grupos")

    @admin.display(description="Grupos")
    def mostrar_grupos(self, obj):
        grupos = obj.groups.order_by("name").values_list("name", flat=True)
        return ", ".join(grupos) or "-"


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ("titulo", "usuario", "leida", "fecha_creacion")
    list_filter = ("leida", "fecha_creacion")
    search_fields = ("titulo", "mensaje", "usuario__username")
