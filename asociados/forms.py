from django import forms

from .models import Asociado
from .validators import validar_nombre_persona, validar_telefono


class AsociadoDatosPropiosForm(forms.Form):
    """Edita solamente los datos personales habilitados para autogestión."""

    nombre = forms.CharField(
        label="Nombre",
        max_length=100,
        validators=[validar_nombre_persona],
    )
    apellido = forms.CharField(
        label="Apellido",
        max_length=100,
        validators=[validar_nombre_persona],
    )
    telefono = forms.CharField(
        label="Teléfono",
        max_length=50,
        required=False,
        validators=[validar_telefono],
    )
    email = forms.EmailField(label="Email", max_length=254, required=False)
    direccion = forms.CharField(
        label="Dirección",
        max_length=255,
        required=False,
    )

    def __init__(self, *args, instance: Asociado | None = None, **kwargs):
        if instance is not None:
            initial = kwargs.setdefault("initial", {})
            for campo in (
                "nombre",
                "apellido",
                "telefono",
                "email",
                "direccion",
            ):
                initial.setdefault(campo, getattr(instance, campo))
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
        self.fields["nombre"].widget.attrs["autofocus"] = True
