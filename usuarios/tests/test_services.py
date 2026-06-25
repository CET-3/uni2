import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from asociados.models import Asociado
from asociados.services import create_asociado
from comercios.models import Comercio
from usuarios.services import (
    ASOCIADO_GROUP,
    COMERCIO_GROUP,
    create_user_for_asociado,
    create_user_for_comercio,
    ensure_default_groups,
)


@pytest.mark.django_db
def test_create_user_for_asociado():
    ensure_default_groups()
    asociado = create_asociado(
        nombre="Ana",
        apellido="Lopez",
        dni="30111222",
        tipo="asociado",
        fecha_alta="2026-05-10",
    )

    assert asociado.usuario is not None
    assert asociado.usuario.username == "30111222"
    assert Group.objects.get(name=ASOCIADO_GROUP) in asociado.usuario.groups.all()


@pytest.mark.django_db
def test_create_user_for_asociado_con_email():
    ensure_default_groups()
    asociado = create_asociado(
        nombre="Ana",
        apellido="Lopez",
        dni="30111222",
        tipo="asociado",
        fecha_alta="2026-05-10",
        email="ana@example.com",
    )

    assert asociado.usuario.email == "ana@example.com"


@pytest.mark.django_db
def test_create_user_for_asociado_ya_tiene_usuario():
    ensure_default_groups()
    asociado = create_asociado(
        nombre="Ana",
        apellido="Lopez",
        dni="30111222",
        tipo="asociado",
        fecha_alta="2026-05-10",
    )

    with pytest.raises(ValueError, match="ya tiene un usuario"):
        create_user_for_asociado(asociado=asociado, password="otra123")


@pytest.mark.django_db
def test_create_user_for_asociado_desde_manual():
    """Verifica que create_user_for_asociado funciona con asociado sin usuario."""
    ensure_default_groups()
    asociado = Asociado.objects.create(
        nombre="Pedro",
        apellido="Garcia",
        dni="30999000",
        tipo="asociado",
        fecha_alta="2026-06-01",
        fecha_inicio_cobro="2026-06-01",
    )

    user = create_user_for_asociado(asociado=asociado, password="secreto123")

    assert asociado.usuario == user
    assert user.username == "30999000"
    assert Group.objects.get(name=ASOCIADO_GROUP) in user.groups.all()


@pytest.mark.django_db
def test_create_user_for_comercio():
    ensure_default_groups()
    from comercios.models import ActividadComercial
    actividad = ActividadComercial.objects.create(nombre="Librería")
    comercio = Comercio.objects.create(
        nombre="Test Comercio",
        actividad_comercial=actividad,
        beneficio_texto="10% off",
    )

    user = create_user_for_comercio(comercio=comercio, password="secreto123")

    assert comercio.usuario == user
    assert user.username == f"com-{comercio.id}"
    assert Group.objects.get(name=COMERCIO_GROUP) in user.groups.all()


@pytest.mark.django_db
def test_create_user_for_comercio_ya_tiene_usuario():
    ensure_default_groups()
    from comercios.models import ActividadComercial
    actividad = ActividadComercial.objects.create(nombre="Librería")
    comercio = Comercio.objects.create(
        nombre="Test Comercio",
        actividad_comercial=actividad,
        beneficio_texto="10% off",
    )
    create_user_for_comercio(comercio=comercio, password="secreto123")

    with pytest.raises(ValueError, match="ya tiene un usuario"):
        create_user_for_comercio(comercio=comercio, password="otra123")

