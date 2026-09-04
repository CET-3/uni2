from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm


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
