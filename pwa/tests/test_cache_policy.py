import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from asociados.services import create_asociado


def cache_control_directives(response):
    return {
        directive.strip().split("=", 1)[0]
        for directive in response.headers["Cache-Control"].lower().split(",")
    }


@pytest.mark.django_db
def test_home_anonima_es_la_unica_clase_de_html_cacheable_publico(client):
    response = client.get(reverse("web:home"))

    assert response.status_code == 200
    assert response.headers["X-Uni2-PWA-Cacheable"] == "public"
    assert "Cookie" in response.headers["Vary"]
    assert "no-cache" in cache_control_directives(response)
    assert "no-store" not in cache_control_directives(response)


@pytest.mark.django_db
def test_misma_home_con_sesion_no_se_marca_publica(client):
    user = get_user_model().objects.create_user(username="persona-pwa")
    client.force_login(user)

    response = client.get(reverse("web:home"))

    assert response.status_code == 200
    assert "X-Uni2-PWA-Cacheable" not in response.headers
    assert {"private", "no-store"} <= cache_control_directives(response)
    assert "Cookie" in response.headers["Vary"]


@pytest.mark.django_db
def test_login_y_logout_no_se_guardan(client):
    login_response = client.get(reverse("usuarios:login"))

    assert login_response.status_code == 200
    assert "X-Uni2-PWA-Cacheable" not in login_response.headers
    assert {"private", "no-store"} <= cache_control_directives(login_response)

    user = get_user_model().objects.create_user(username="logout-pwa")
    client.force_login(user)
    logout_response = client.post(reverse("usuarios:logout"))

    assert logout_response.status_code == 302
    assert "X-Uni2-PWA-Cacheable" not in logout_response.headers
    assert {"private", "no-store"} <= cache_control_directives(logout_response)


@pytest.mark.django_db
def test_credencial_autenticada_es_privada_y_no_store(client):
    asociado = create_asociado(
        nombre="Juana",
        apellido="Segura",
        dni="40888777",
        tipo="asociado",
        fecha_alta="2026-07-01",
    )
    client.force_login(asociado.usuario)

    response = client.get(reverse("asociados:credencial"))

    assert response.status_code == 200
    assert "X-Uni2-PWA-Cacheable" not in response.headers
    assert {"private", "no-store"} <= cache_control_directives(response)
    assert "Cookie" in response.headers["Vary"]


def test_manifest_json_no_recibe_politica_de_html(client):
    response = client.get(reverse("pwa:manifest"))

    assert "X-Uni2-PWA-Cacheable" not in response.headers
    assert "Vary" not in response.headers
