import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command

from asociados.models import Asociado
from comercios.models import Comercio
from contenidos.models import CategoriaProductoServicio, ProductoServicio
from gestion.permissions import GESTION_COBRAR_CUOTAS, GESTION_IMPORTAR_ASOCIADOS


@pytest.mark.django_db
def test_carga_inicial_crea_usuarios_de_prueba():
    call_command("carga_inicial")
    call_command("carga_inicial")

    user_model = get_user_model()
    admin = user_model.objects.get(username="admin")
    atencion_user = user_model.objects.get(username="atencion")
    asociado_user = user_model.objects.get(username="asociado")
    comercio_user = user_model.objects.get(username="comercio")

    assert admin.groups.filter(name="Administradores").exists()
    assert atencion_user.groups.filter(name="Atención de mutual").exists()
    assert atencion_user.groups.filter(name="Asociados").exists()
    assert atencion_user.has_perm(GESTION_COBRAR_CUOTAS)
    assert not atencion_user.has_perm(GESTION_IMPORTAR_ASOCIADOS)
    assert asociado_user.groups.filter(name="Asociados").exists()
    assert comercio_user.groups.filter(name="Comercios").exists()
    assert Group.objects.filter(name="Atención de mutual").exists()
    assert Asociado.objects.get(dni="40111223").usuario == atencion_user
    assert Asociado.objects.get(dni="40111222").usuario == asociado_user
    assert Comercio.objects.get(nombre="Librería Sur").usuario == comercio_user
    assert CategoriaProductoServicio.objects.filter(nombre="Impresiones y fotocopias").exists()
    assert ProductoServicio.objects.filter(nombre="Fotocopia simple").exists()
