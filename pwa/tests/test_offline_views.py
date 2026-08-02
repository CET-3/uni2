import pytest
from django.urls import resolve, reverse

from asociados.services import create_asociado


OFFLINE_ROUTES = {
    "offline": "/sin-conexion/",
    "offline_action": "/sin-conexion/accion-no-enviada/",
    "offline_credential": "/sin-conexion/credencial/",
}


@pytest.mark.parametrize(("name", "path"), OFFLINE_ROUTES.items())
def test_rutas_offline_son_estables(name, path):
    assert reverse(f"pwa:{name}") == path
    assert resolve(path).view_name == f"pwa:{name}"


@pytest.mark.parametrize("name", OFFLINE_ROUTES)
def test_shell_offline_es_html_revalidable_y_no_cache_publica(client, name):
    response = client.get(reverse(f"pwa:{name}"))

    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("text/html")
    assert response.headers["Cache-Control"] == "no-cache, max-age=0, must-revalidate"
    assert "Cookie" in response.headers["Vary"]
    assert "X-Uni2-PWA-Cacheable" not in response.headers


@pytest.mark.django_db
def test_shells_offline_neutralizan_sesion_y_datos_privados(client):
    asociado = create_asociado(
        nombre="NombrePrivadoPWA",
        apellido="ApellidoPrivadoPWA",
        dni="40999111",
        tipo="asociado",
        fecha_alta="2026-07-01",
        email="privado-pwa@example.test",
        direccion="Direccion privada 123",
    )
    client.force_login(asociado.usuario)

    private_values = (
        asociado.nombre,
        asociado.apellido,
        asociado.dni,
        asociado.email,
        asociado.direccion,
        str(asociado.token_credencial),
        asociado.usuario.username,
    )
    for name in OFFLINE_ROUTES:
        content = client.get(reverse(f"pwa:{name}")).content.decode()
        assert 'data-pwa-owner-source=""' in content
        assert "csrfmiddlewaretoken" not in content
        assert "Salir" not in content
        for private_value in private_values:
            assert private_value not in content


def test_shell_offline_general_explica_que_no_guarda_contenido_privado(client):
    content = client.get(reverse("pwa:offline")).content.decode()

    assert "Sin conexión" in content
    assert "contenido privado" in content


def test_shell_de_mutacion_confirma_que_no_hay_pendiente(client):
    content = client.get(reverse("pwa:offline_action")).content.decode()

    assert "La operación no se envió" in content
    assert "no quedó guardado ni pendiente" in content


def test_shell_de_credencial_no_contiene_una_credencial_embebida(client):
    content = client.get(reverse("pwa:offline_credential")).content.decode()

    assert "Buscando la credencial guardada" in content
    assert "data-offline-credential-name" in content
    assert "data-offline-credential-token" in content
    assert "value=" not in content
