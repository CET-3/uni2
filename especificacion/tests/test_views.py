import pytest
from django.contrib.auth.models import Permission, User
from django.urls import reverse


VER_ESPECIFICACION = "gestion.ver_especificacion"


def _usuario_con_permiso():
    user = User.objects.create_user(username="test", password="test")
    user.user_permissions.add(Permission.objects.get(codename=VER_ESPECIFICACION.split(".", 1)[1]))
    return user


@pytest.mark.django_db
class TestEspecificacionIndice:
    def test_indice_redirect_si_no_autenticado(self, client):
        response = client.get(reverse("especificacion:indice"))
        assert response.status_code in (302, 403)

    def test_indice_redirect_si_no_permiso(self, client):
        user = User.objects.create_user(username="test", password="test")
        client.force_login(user)
        response = client.get(reverse("especificacion:indice"))
        assert response.status_code in (302, 403)

    def test_indice_ok_con_permiso(self, client):
        client.force_login(_usuario_con_permiso())
        response = client.get(reverse("especificacion:indice"))
        assert response.status_code == 200
        content = response.content.decode()
        assert "Especificación Uni2" in content
        assert "/especificacion/guia-windows-python-django.md/" in content


@pytest.mark.django_db
class TestEspecificacionArchivo:
    def test_archivo_valido_ok(self, client):
        client.force_login(_usuario_con_permiso())
        response = client.get(reverse("especificacion:archivo", kwargs={"ruta": "proyecto/index.md"}))
        assert response.status_code == 200

    def test_guia_de_inicio_se_sirve_desde_el_visualizador(self, client):
        client.force_login(_usuario_con_permiso())
        response = client.get(
            reverse(
                "especificacion:archivo",
                kwargs={"ruta": "guia-windows-python-django.md"},
            )
        )
        assert response.status_code == 200
        assert "Instalar Python" in response.content.decode()

    def test_archivo_inexistente_404(self, client):
        client.force_login(_usuario_con_permiso())
        response = client.get(reverse("especificacion:archivo", kwargs={"ruta": "no-existe.md"}))
        assert response.status_code == 404

    def test_archivo_path_traversal_rechazado(self, client):
        client.force_login(_usuario_con_permiso())
        response = client.get(reverse("especificacion:archivo", kwargs={"ruta": "../manage.py"}))
        assert response.status_code == 404
