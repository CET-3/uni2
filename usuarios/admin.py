from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group, User

from auditoria.admin_mixins import AuditoriaAdminMixin
from .admin_access import Uni2AdminSite
from .roles import ADMINISTRADOR_APP_GROUP
from .models import Notificacion


admin.site.__class__ = Uni2AdminSite

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class Uni2UserAdmin(AuditoriaAdminMixin, UserAdmin):
    allow_superuser_delete = True
    audit_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "is_superuser",
        "groups",
        "user_permissions",
    )
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "mostrar_grupos")

    @admin.display(description="Grupos")
    def mostrar_grupos(self, obj):
        grupos = obj.groups.order_by("name").values_list("name", flat=True)
        return ", ".join(grupos) or "-"

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser or obj is None:
            return super().get_fieldsets(request, obj)
        return (
            (None, {"fields": ("username", "password")}),
            ("Información personal", {"fields": ("first_name", "last_name", "email")}),
            ("Acceso", {"fields": ("is_active", "is_staff", "groups")}),
            ("Fechas importantes", {"fields": ("last_login", "date_joined")}),
        )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "groups" and not request.user.is_superuser:
            kwargs["queryset"] = Group.objects.exclude(name=ADMINISTRADOR_APP_GROUP)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def has_change_permission(self, request, obj=None):
        permitido = super().has_change_permission(request, obj)
        if not permitido or request.user.is_superuser or obj is None:
            return permitido
        return not (
            obj.is_superuser
            or obj.groups.filter(name=ADMINISTRADOR_APP_GROUP).exists()
        )


@admin.register(Group)
class Uni2GroupAdmin(AuditoriaAdminMixin, GroupAdmin):
    audit_fields = ("name", "permissions")

    def has_delete_permission(self, request, obj=None):
        # Los grupos se administran con los permisos estándar de Django.
        return GroupAdmin.has_delete_permission(self, request, obj)


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ("titulo", "usuario", "leida", "fecha_creacion")
    list_filter = ("leida", "fecha_creacion")
    search_fields = ("titulo", "mensaje", "usuario__username")
