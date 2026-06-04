from django import forms
from django.contrib import admin

from .services import calculate_fecha_inicio_cobro
from .models import Asociado, CicloLectivo, Curso


@admin.register(CicloLectivo)
class CicloLectivoAdmin(admin.ModelAdmin):
    list_display = ("anio",)
    search_fields = ("anio",)


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ("anio", "curso", "division", "turno", "activo")
    list_filter = ("division", "turno", "activo")
    search_fields = ("anio", "curso")


class AsociadoAdminForm(forms.ModelForm):
    class Meta:
        model = Asociado
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fecha_inicio_cobro"].required = False
        self.fields["curso_actual"].required = False

    def clean(self):
        cleaned_data = super().clean()
        fecha_alta = cleaned_data.get("fecha_alta")
        fecha_inicio_cobro = cleaned_data.get("fecha_inicio_cobro")

        if fecha_alta and not fecha_inicio_cobro:
            cleaned_data["fecha_inicio_cobro"] = calculate_fecha_inicio_cobro(fecha_alta)
            self.instance.fecha_inicio_cobro = cleaned_data["fecha_inicio_cobro"]

        return cleaned_data


@admin.register(Asociado)
class AsociadoAdmin(admin.ModelAdmin):
    form = AsociadoAdminForm
    list_display = (
        "numero_asociado",
        "apellido",
        "nombre",
        "dni",
        "tipo",
        "estado",
        "curso_actual",
        "usuario",
        "last_login_display",
    )
    list_filter = ("estado", "tipo", "curso_actual")
    search_fields = ("apellido", "nombre", "dni", "numero_asociado")
    readonly_fields = ("numero_asociado", "token_credencial")
    fieldsets = (
        (
            "Datos personales",
            {
                "fields": (
                    "nombre",
                    "apellido",
                    "dni",
                    "tipo",
                    "fecha_nacimiento",
                    "email",
                    "telefono",
                    "usuario",
                )
            },
        ),
        (
            "Datos mutuales",
            {
                "fields": (
                    "numero_asociado",
                    "estado",
                    "curso_actual",
                    "fecha_alta",
                    "fecha_inicio_cobro",
                    "fecha_baja",
                    "motivo_baja",
                    "token_credencial",
                )
            },
        ),
    )

    @admin.display(description="Ultimo acceso")
    def last_login_display(self, obj):
        return obj.usuario.last_login if obj.usuario else None
