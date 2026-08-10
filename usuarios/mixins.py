class CredentialPrivacyHeadersMixin:
    """Evita que respuestas vinculadas a un token queden almacenadas o referidas."""

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        response.headers["Cache-Control"] = "private, no-store"
        response.headers["Referrer-Policy"] = "same-origin"
        return response
