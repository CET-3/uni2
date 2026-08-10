import pytest
from django.contrib.auth import get_user_model

from asociados.models import Asociado
from auditoria.models import EventoAuditoria
from usuarios.services import create_user_for_asociado, ensure_default_groups


@pytest.mark.django_db
def test_crear_usuario_y_vincular_asociado_comparten_operacion_sin_password():
    ensure_default_groups()
    actor = get_user_model().objects.create_user(username="administradora", password="secreto123")
    asociado = Asociado.objects.create(
        nombre="Julia",
        apellido="Campos",
        dni="40111999",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta="2026-08-09",
        fecha_inicio_cobro="2026-08-01",
    )

    user = create_user_for_asociado(
        asociado=asociado,
        password="clave-inicial",
        actor=actor,
    )

    eventos = EventoAuditoria.objects.filter(actor=actor).order_by("id")
    assert eventos.count() == 2
    assert len(set(eventos.values_list("operacion_id", flat=True))) == 1
    assert set(eventos.values_list("entidad", "accion")) == {
        ("auth.User", EventoAuditoria.ACCION_CREAR),
        ("asociados.Asociado", EventoAuditoria.ACCION_VINCULAR),
    }
    assert all("password" not in evento.cambios for evento in eventos)
    assert all("clave-inicial" not in str(evento.cambios) for evento in eventos)
    assert user.groups.filter(name="Asociados").exists()
