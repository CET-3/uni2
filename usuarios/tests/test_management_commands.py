import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

from asociados.models import Asociado
from comercios.models import ActividadComercial, Comercio
from contenidos.models import CategoriaProductoServicio, ProductoServicio
from gestion.permissions import GESTION_COBRAR_CUOTAS, GESTION_IMPORTAR_ASOCIADOS, GESTION_VER_DESIGN_SYSTEM


SERVICIOS_VERCEL = {"Fotocopias", "Uniformes", "Bicicleta solidaria", "Cuadernillos y anillado"}
RUBROS_VERCEL = {"Gastronomía", "Actividad física", "Belleza", "Vestimenta", "Educación", "Tecnología y accesorios"}
COMERCIOS_VERCEL = {"Alto Drugstore", "Librería Muñoz", "Atenas Gimnasio", "Andromeda Studio", "Carolina's Closet", "Techno Store"}


@pytest.mark.django_db
@override_settings(ALLOW_DEMO_DATA=False)
def test_carga_inicial_rechaza_entornos_sin_datos_demo():
    with pytest.raises(CommandError, match="no debe ejecutarse sobre producción"):
        call_command("carga_inicial")

    assert not get_user_model().objects.filter(username="admin").exists()


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
    assert atencion_user.has_perm(GESTION_VER_DESIGN_SYSTEM)
    assert admin.has_perm(GESTION_VER_DESIGN_SYSTEM)
    assert not atencion_user.has_perm(GESTION_IMPORTAR_ASOCIADOS)
    assert asociado_user.groups.filter(name="Asociados").exists()
    assert comercio_user.groups.filter(name="Comercios").exists()
    assert Group.objects.filter(name="Atención de mutual").exists()
    assert Asociado.objects.get(dni="40111223").usuario == atencion_user
    assert Asociado.objects.get(dni="40111222").usuario == asociado_user
    assert Comercio.objects.get(nombre="Librería Sur").usuario == comercio_user


@pytest.mark.django_db
def test_carga_inicial_crea_servicios_vercel():
    call_command("carga_inicial")
    nombres = set(CategoriaProductoServicio.objects.values_list("nombre", flat=True))
    assert SERVICIOS_VERCEL.issubset(nombres), f"Faltan servicios: {SERVICIOS_VERCEL - nombres}"
    assert ProductoServicio.objects.filter(categoria__nombre="Fotocopias").exists()


@pytest.mark.django_db
def test_carga_inicial_crea_rubros_vercel():
    call_command("carga_inicial")
    nombres = set(ActividadComercial.objects.values_list("nombre", flat=True))
    assert RUBROS_VERCEL.issubset(nombres), f"Faltan rubros: {RUBROS_VERCEL - nombres}"


@pytest.mark.django_db
def test_carga_inicial_crea_comercios_vercel():
    call_command("carga_inicial")
    nombres = set(Comercio.objects.values_list("nombre", flat=True))
    assert COMERCIOS_VERCEL.issubset(nombres), f"Faltan comercios: {COMERCIOS_VERCEL - nombres}"
