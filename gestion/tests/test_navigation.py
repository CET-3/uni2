from django.test import RequestFactory
from django.urls import reverse

from gestion.navigation import add_asociados_return, get_asociado_detail_url, get_asociados_return_url


def test_retorno_asociados_conserva_filtros_locales():
    return_url = f"{reverse('gestion:asociados')}?q=Campos&estado=activo"
    request = RequestFactory().get(reverse("gestion:asociado_detalle", args=[1]), {"volver": return_url})

    assert get_asociados_return_url(request) == return_url


def test_retorno_asociados_rechaza_destinos_externos_y_otras_pantallas():
    factory = RequestFactory()

    external_request = factory.get("/", {"volver": "https://example.com/engaño"})
    other_view_request = factory.get("/", {"volver": reverse("web:home")})

    assert get_asociados_return_url(external_request) == reverse("gestion:asociados")
    assert get_asociados_return_url(other_view_request) == reverse("gestion:asociados")


def test_urls_operativas_transportan_el_retorno_codificado():
    return_url = f"{reverse('gestion:asociados')}?q=Ríos"

    edit_url = add_asociados_return(reverse("gestion:asociado_editar", args=[7]), return_url)
    detail_url = get_asociado_detail_url(7, return_url)

    assert edit_url.endswith("?volver=%2Fgestion%2Fasociados%2F%3Fq%3DR%C3%ADos")
    assert detail_url.endswith("?volver=%2Fgestion%2Fasociados%2F%3Fq%3DR%C3%ADos")
