from django.utils.cache import patch_cache_control, patch_vary_headers


PUBLIC_WEB_VIEW_NAMES = {
    "actividad_comercial_detalle",
    "categoria_detalle",
    "comercio_detalle",
    "comercios",
    "home",
    "inicio",
    "producto_servicio_detalle",
    "productos_servicios",
}

OFFLINE_SHELL_VIEW_NAMES = {
    "offline",
    "offline_action",
    "offline_credential",
}


class PWACacheControlMiddleware:
    """Explicita qué HTML puede persistir el service worker.

    La ausencia de ``X-Uni2-PWA-Cacheable: public`` siempre significa que una
    navegación HTML no se puede incorporar al caché público de la PWA.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if not self._is_html(response):
            return response

        patch_vary_headers(response, ("Cookie",))

        if self._is_offline_shell(request, response):
            response.headers["Cache-Control"] = "no-cache, max-age=0, must-revalidate"
            return response

        if self._is_public_navigation(request, response):
            response.headers["X-Uni2-PWA-Cacheable"] = "public"
            response.headers["Cache-Control"] = "no-cache, max-age=0, must-revalidate"
            return response

        response.headers.pop("X-Uni2-PWA-Cacheable", None)
        patch_cache_control(
            response,
            private=True,
            no_store=True,
            no_cache=True,
            max_age=0,
            must_revalidate=True,
        )
        return response

    @staticmethod
    def _is_html(response):
        content_type = response.headers.get("Content-Type", "")
        return content_type.lower().split(";", 1)[0].strip() == "text/html"

    @staticmethod
    def _is_offline_shell(request, response):
        match = request.resolver_match
        return (
            request.method == "GET"
            and response.status_code == 200
            and match is not None
            and match.namespace == "pwa"
            and match.url_name in OFFLINE_SHELL_VIEW_NAMES
        )

    @staticmethod
    def _is_public_navigation(request, response):
        match = request.resolver_match
        user = getattr(request, "user", None)
        return (
            request.method == "GET"
            and response.status_code == 200
            and user is not None
            and not user.is_authenticated
            and match is not None
            and match.namespace == "web"
            and match.url_name in PUBLIC_WEB_VIEW_NAMES
        )
