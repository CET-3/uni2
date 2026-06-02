from django.contrib import admin

from .models import Beneficio


@admin.register(Beneficio)
class BeneficioAdmin(admin.ModelAdmin):
    list_display = ("titulo", "activo", "orden")
    list_filter = ("activo",)
