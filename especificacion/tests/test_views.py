import pytest
from django.contrib.auth.models import User
from django.urls import reverse


@pytest.mark.django_db
class TestEspecificacionIndice:
    def test_indice_redirect_si_no_autenticado(self, client):
        response = client.get(reverse("especificacion:indice"))
        assert response.status_code in (302, 403)

    def test_indice_redirect_si_no_staff(self, client):
        user = User.objects.create_user(username="test", password="test")
        client.force_login(user)
        response = client.get(reverse("especificacion:indice"))
        assert response.status_code in (302, 403)

    def test_indice_ok_para_staff(self, client):
        user = User.objects.create_user(username="staff", password="test", is_staff=True)
        client.force_login(user)
        response = client.get(reverse("especificacion:indice"))
        assert response.status_code == 200
        assert "Especificación Uni2" in response.content.decode()


@pytest.mark.django_db
class TestEspecificacionArchivo:
    def test_archivo_valido_ok(self, client):
        user = User.objects.create_user(username="staff", password="test", is_staff=True)
        client.force_login(user)
        response = client.get(reverse("especificacion:archivo", kwargs={"ruta": "proyecto/index.md"}))
        assert response.status_code == 200

    def test_archivo_inexistente_404(self, client):
        user = User.objects.create_user(username="staff", password="test", is_staff=True)
        client.force_login(user)
        response = client.get(reverse("especificacion:archivo", kwargs={"ruta": "no-existe.md"}))
        assert response.status_code == 404

    def test_archivo_path_traversal_rechazado(self, client):
        user = User.objects.create_user(username="staff", password="test", is_staff=True)
        client.force_login(user)
        response = client.get(reverse("especificacion:archivo", kwargs={"ruta": "../manage.py"}))
        assert response.status_code == 404
