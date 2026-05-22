import pytest
from django.contrib.auth.models import Group

from asociados.services import create_asociado
from usuarios.services import ASOCIADO_GROUP, create_user_for_asociado, ensure_default_groups


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

    user = create_user_for_asociado(asociado=asociado, password="secreto123")

    assert asociado.usuario == user
    assert user.username == "30111222"
    assert Group.objects.get(name=ASOCIADO_GROUP) in user.groups.all()

