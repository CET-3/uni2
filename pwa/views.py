import json
import re
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.http import require_GET


DEFAULT_BUILD_ID = "development"


def _cache_identifier(configured_id):
    normalized_id = re.sub(r"[^a-zA-Z0-9._-]", "-", configured_id).strip("-")
    return normalized_id or DEFAULT_BUILD_ID


def _build_id():
    """Devuelve un identificador seguro para usar dentro de nombres de caché."""

    return _cache_identifier(str(getattr(settings, "PWA_BUILD_ID", DEFAULT_BUILD_ID)))


def _private_data_epoch():
    return _cache_identifier(
        str(getattr(settings, "PWA_PRIVATE_DATA_EPOCH", DEFAULT_BUILD_ID))
    )


def _icon_url(filename):
    return static(f"{settings.PWA_ICON_DIRECTORY}/{filename}")


def _precache_urls():
    shell_urls = [
        reverse("pwa:offline"),
        reverse("pwa:offline_action"),
        reverse("pwa:offline_credential"),
        static("css/uni2-design-system.css"),
        static("js/uni2-theme.js"),
        static("js/uni2-carousel.js"),
        static("vendor/bootstrap/5.3.3/css/bootstrap.min.css"),
        static("vendor/bootstrap/5.3.3/js/bootstrap.bundle.min.js"),
        static("vendor/bootstrap-icons/1.11.3/font/bootstrap-icons.min.css"),
        static("vendor/bootstrap-icons/1.11.3/font/fonts/bootstrap-icons.woff"),
        static("vendor/bootstrap-icons/1.11.3/font/fonts/bootstrap-icons.woff2"),
        static("vendor/qrcode-generator/1.4.4/qrcode.min.js"),
        static("pwa/uni2-pwa.js"),
        static("pwa/uni2-private-storage.js"),
        static("pwa/uni2-credential.js"),
        _icon_url("icon-192.png"),
        _icon_url("icon-512.png"),
    ]
    configured_urls = getattr(settings, "PWA_PRECACHE_URLS", ())
    return list(dict.fromkeys([*shell_urls, *configured_urls]))


def _offline_context():
    # Estos documentos se guardan completos en Cache Storage. El contexto se
    # neutraliza aunque la primera descarga ocurra durante una sesión iniciada.
    return {
        "user": AnonymousUser(),
        "messages": (),
        "show_site_chrome": False,
    }


def _public_media_origin():
    """Normaliza el dominio público de media sin ampliar el allowlist."""

    configured_domain = str(getattr(settings, "AWS_S3_CUSTOM_DOMAIN", "") or "").strip()
    if not configured_domain:
        return ""

    candidate = configured_domain if "://" in configured_domain else f"https://{configured_domain}"
    parsed = urlsplit(candidate)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username
        or parsed.password
    ):
        return ""
    return f"{parsed.scheme}://{parsed.netloc}"


@require_GET
def manifest(request):
    data = {
        "id": "/",
        "name": settings.PWA_APP_NAME,
        "short_name": settings.PWA_SHORT_NAME,
        "description": settings.PWA_DESCRIPTION,
        "lang": "es-AR",
        "dir": "ltr",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "prefer_related_applications": False,
        "theme_color": settings.PWA_THEME_COLOR,
        "background_color": settings.PWA_BACKGROUND_COLOR,
        "icons": [
            {
                "src": _icon_url("icon-192.png"),
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": _icon_url("icon-512.png"),
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": _icon_url("icon-maskable-192.png"),
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "maskable",
            },
            {
                "src": _icon_url("icon-maskable-512.png"),
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "maskable",
            },
        ],
        "shortcuts": [
            {
                "name": "Productos y servicios",
                "short_name": "Productos",
                "url": reverse("web:productos_servicios"),
            },
            {
                "name": "Comercios adheridos",
                "short_name": "Comercios",
                "url": reverse("web:comercios"),
            },
            {
                "name": "Ingresar",
                "short_name": "Ingresar",
                "url": reverse("usuarios:login"),
            },
        ],
    }
    response = JsonResponse(data, content_type="application/manifest+json")
    response.headers["Cache-Control"] = "no-cache, max-age=0, must-revalidate"
    return response


@require_GET
def service_worker(request):
    precache_urls_json = json.dumps(_precache_urls())
    source = render_to_string(
        "pwa/service-worker.js",
        {
            "pwa_build_id_json": json.dumps(_build_id()),
            "pwa_private_data_epoch_json": json.dumps(_private_data_epoch()),
            "pwa_offline_url_json": json.dumps(reverse("pwa:offline")),
            "pwa_offline_action_url_json": json.dumps(reverse("pwa:offline_action")),
            "pwa_offline_credential_url_json": json.dumps(reverse("pwa:offline_credential")),
            "pwa_credential_url_json": json.dumps(reverse("asociados:credencial")),
            "pwa_precache_urls_json_literal": json.dumps(precache_urls_json),
            "pwa_static_url_json": json.dumps(settings.STATIC_URL),
            "pwa_media_url_json": json.dumps(settings.MEDIA_URL),
            "pwa_public_media_origin_json": json.dumps(_public_media_origin()),
        },
    )
    # El worker no usa sesión ni contexto de navegación. Renderizarlo sin
    # RequestContext evita trabajo innecesario y un ``Vary: Cookie`` engañoso.
    response = HttpResponse(source, content_type="application/javascript")
    response.headers["Cache-Control"] = "no-cache, max-age=0, must-revalidate"
    response.headers["Service-Worker-Allowed"] = "/"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@require_GET
def offline(request):
    return render(request, "pwa/offline.html", _offline_context())


@require_GET
def offline_action(request):
    return render(request, "pwa/offline_action.html", _offline_context())


@require_GET
def offline_credential(request):
    return render(request, "pwa/offline_credential.html", _offline_context())
