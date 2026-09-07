from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    SetPasswordForm,
)
from django.core.exceptions import ValidationError

from asociados.validators import normalizar_documento


class Uni2AuthenticationForm(AuthenticationForm):
    """Presenta el login con los controles visuales y ayudas de Uni2."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control",
                "autocomplete": "username",
                "placeholder": "Ingresá tu usuario",
                "autofocus": True,
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "class": "form-control",
                "autocomplete": "current-password",
                "placeholder": "Ingresá tu contraseña",
            }
        )


class Uni2PasswordChangeForm(PasswordChangeForm):
    """Aplica los controles visuales de Uni2 al cambio de contraseña."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
        self.fields["old_password"].widget.attrs["autofocus"] = True


class RecuperarContrasenaForm(forms.Form):
    dni = forms.CharField(label="DNI o documento", max_length=30)
    email = forms.EmailField(label="Email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["dni"].widget.attrs.update(
            {"class": "form-control", "autocomplete": "username"}
        )
        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "autocomplete": "email"}
        )
        self.fields["dni"].widget.attrs["autofocus"] = True

    def clean_dni(self):
        try:
            return normalizar_documento(self.cleaned_data["dni"])
        except ValidationError as error:
            raise forms.ValidationError(error.messages) from error


class Uni2SetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update(
                {"class": "form-control", "autocomplete": "new-password"}
            )
        self.fields["new_password1"].widget.attrs["autofocus"] = True
