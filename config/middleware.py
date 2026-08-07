import base64
import binascii
import secrets

from django.conf import settings
from django.http import HttpResponse
from django.utils.cache import patch_vary_headers


class StagingAccessMiddleware:
    """Protege el clon de datos antes de ejecutar cualquier vista Django."""

    PUBLIC_PWA_PATHS = frozenset(
        {
            "/manifest.webmanifest",
            "/service-worker.js",
            "/sin-conexion/",
            "/sin-conexion/accion-no-enviada/",
            "/sin-conexion/credencial/",
        }
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._is_public_pwa_resource(request):
            return self._protect_response(self.get_response(request))

        credentials = self._credentials(request)
        expected = (
            settings.UNI2_STAGING_ACCESS_USERNAME,
            settings.UNI2_STAGING_ACCESS_PASSWORD,
        )
        if credentials is None or not all(
            secrets.compare_digest(received, configured)
            for received, configured in zip(credentials, expected, strict=True)
        ):
            response = HttpResponse(
                "Este entorno de prueba requiere autorización.",
                status=401,
                content_type="text/plain; charset=utf-8",
            )
            response.headers["WWW-Authenticate"] = 'Basic realm="UNI2 Staging", charset="UTF-8"'
            return self._protect_response(response)

        if not self._staging_data_is_ready(request):
            response = HttpResponse(
                "La copia de datos de staging todavía no está habilitada.",
                status=503,
                content_type="text/plain; charset=utf-8",
            )
            response.headers["Retry-After"] = "60"
            return self._protect_response(response)

        response = self.get_response(request)
        return self._protect_response(response)

    @classmethod
    def _is_public_pwa_resource(cls, request):
        """Deja instalar el shell neutro sin abrir vistas ni datos del clon."""

        if request.method not in {"GET", "HEAD"}:
            return False

        path = request.path_info
        static_prefix = f"/{settings.STATIC_URL.lstrip('/')}"
        return path in cls.PUBLIC_PWA_PATHS or path.startswith(static_prefix)

    @staticmethod
    def _credentials(request):
        authorization = request.headers.get("Authorization", "")
        scheme, separator, encoded = authorization.partition(" ")
        if separator != " " or scheme.lower() != "basic" or not encoded:
            return None

        try:
            decoded = base64.b64decode(encoded, validate=True).decode("utf-8")
        except (binascii.Error, UnicodeDecodeError):
            return None

        username, separator, password = decoded.partition(":")
        if separator != ":":
            return None
        return username, password

    @staticmethod
    def _staging_data_is_ready(request):
        from django.db import DatabaseError

        from usuarios.models import EstadoDatosStaging

        try:
            state = EstadoDatosStaging.objects.filter(
                clave=EstadoDatosStaging.CLAVE_ACTUAL,
                refresh_id=settings.PWA_PRIVATE_DATA_EPOCH,
            ).first()
        except DatabaseError:
            return False

        request.uni2_staging_data_state = state
        return state is not None

    @staticmethod
    def _protect_response(response):
        response.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
        response.headers["Cache-Control"] = "private, no-store"
        patch_vary_headers(response, ("Authorization",))
        return response
