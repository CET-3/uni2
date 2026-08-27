from django import forms
from django.core.exceptions import NON_FIELD_ERRORS

from asociados.models import ClasificacionAdherente, Curso
from asociados.validators import (
    normalizar_documento,
    validar_nombre_persona,
    validar_telefono,
)


class SolicitudAsociacionForm(forms.Form):
    nombre = forms.CharField(max_length=100, validators=[validar_nombre_persona])
    apellido = forms.CharField(max_length=100, validators=[validar_nombre_persona])
    dni = forms.CharField(label="DNI o documento", max_length=30)
    email = forms.EmailField(label="Correo electrónico")
    telefono = forms.CharField(max_length=30, validators=[validar_telefono])
    direccion = forms.CharField(label="Domicilio", max_length=255)
    es_estudiante_cet3 = forms.ChoiceField(
        label="¿Sos estudiante del CET 3?",
        choices=(("si", "Sí"), ("no", "No")),
        widget=forms.RadioSelect,
    )
    curso_actual = forms.ModelChoiceField(
        label="Curso y división",
        queryset=Curso.objects.none(),
        required=False,
        empty_label="Elegí tu curso",
    )
    clasificacion_adherente = forms.ModelChoiceField(
        label="Categoría",
        queryset=ClasificacionAdherente.objects.none(),
        required=False,
        empty_label="Elegí una categoría",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["curso_actual"].queryset = Curso.objects.filter(activo=True)
        self.fields["clasificacion_adherente"].queryset = (
            ClasificacionAdherente.objects.filter(activa=True).order_by("orden", "nombre")
        )
        for nombre, campo in self.fields.items():
            if nombre == "es_estudiante_cet3":
                campo.widget.attrs["class"] = "form-check-input"
            else:
                campo.widget.attrs["class"] = "form-select" if isinstance(
                    campo.widget, forms.Select
                ) else "form-control"
        if not self.is_bound:
            self.fields["nombre"].widget.attrs["autofocus"] = True

    def full_clean(self):
        super().full_clean()
        if not self.is_bound:
            return

        for nombre in self._errors:
            if nombre not in self.fields:
                continue
            campo = self.fields[nombre]
            if isinstance(campo.widget, forms.RadioSelect):
                continue

            clases = campo.widget.attrs.get("class", "").split()
            if "is-invalid" not in clases:
                clases.append("is-invalid")
            campo.widget.attrs["class"] = " ".join(clases)
            campo.widget.attrs["aria-invalid"] = "true"

            error_id = f"{self[nombre].auto_id}-errors"
            descripciones = campo.widget.attrs.get("aria-describedby", "").split()
            if error_id not in descripciones:
                descripciones.append(error_id)
            campo.widget.attrs["aria-describedby"] = " ".join(descripciones)

    @property
    def tiene_errores_de_campo(self):
        return any(nombre != NON_FIELD_ERRORS for nombre in self.errors)

    def clean_dni(self):
        dni = self.cleaned_data["dni"].strip()
        normalizar_documento(dni)
        return dni

    def clean(self):
        cleaned_data = super().clean()
        condicion = cleaned_data.get("es_estudiante_cet3")
        if condicion == "si":
            cleaned_data["es_estudiante_cet3"] = True
            cleaned_data["clasificacion_adherente"] = None
            if cleaned_data.get("curso_actual") is None:
                self.add_error("curso_actual", "Elegí tu curso.")
        elif condicion == "no":
            cleaned_data["es_estudiante_cet3"] = False
            cleaned_data["curso_actual"] = None
            if cleaned_data.get("clasificacion_adherente") is None:
                self.add_error(
                    "clasificacion_adherente",
                    "Elegí una categoría.",
                )
        return cleaned_data
