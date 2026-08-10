from urllib.parse import urlencode, urlsplit, urlunsplit

from django.urls import reverse


RETURN_PARAMETER = "volver"


def get_asociados_return_url(request):
    """Devuelve únicamente una URL local de la consulta de asociados."""
    candidate = request.POST.get(RETURN_PARAMETER) or request.GET.get(RETURN_PARAMETER)
    default_url = reverse("gestion:asociados")
    if not candidate:
        return default_url

    parsed = urlsplit(candidate)
    if parsed.scheme or parsed.netloc or parsed.path != default_url:
        return default_url

    return urlunsplit(("", "", parsed.path, parsed.query, ""))


def add_asociados_return(url, return_url):
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}{urlencode({RETURN_PARAMETER: return_url})}"


def get_asociado_detail_url(asociado_id, return_url):
    detail_url = reverse("gestion:asociado_detalle", args=[asociado_id])
    return add_asociados_return(detail_url, return_url)
