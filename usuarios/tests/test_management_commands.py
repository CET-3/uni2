import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from asociados.models import Asociado
from comercios.models import Comercio


@pytest.mark.django_db
def test_carga_inicial_crea_usuarios_de_prueba():
    call_command("carga_inicial")
    call_command("carga_inicial")

    user_model = get_user_model()
    admin = user_model.objects.get(username="admin")
    asociado_user = user_model.objects.get(username="asociado")
    comercio_user = user_model.objects.get(username="comercio")

    assert admin.groups.filter(name="Administradores").exists()
    assert asociado_user.groups.filter(name="Asociados").exists()
    assert comercio_user.groups.filter(name="Comercios").exists()
    assert Asociado.objects.get(dni="40111222").usuario == asociado_user
    assert Comercio.objects.get(nombre="Librería Sur").usuario == comercio_user
