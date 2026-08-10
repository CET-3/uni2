import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from auditoria.models import EventoAuditoria
from auditoria.services import registrar_evento


@pytest.mark.django_db
def test_evento_auditoria_es_inmutable():
    actor = get_user_model().objects.create_user(username="auditora", password="secreto123")
    evento = registrar_evento(
        actor=actor,
        accion=EventoAuditoria.ACCION_CREAR,
        entidad="asociados.Asociado",
        objeto_id="1",
        objeto_descripcion="Pérez, Ana",
        cambios={},
        origen=EventoAuditoria.ORIGEN_GESTION,
    )

    evento.objeto_descripcion = "Descripción cambiada"
    with pytest.raises(ValidationError, match="no se pueden modificar"):
        evento.save()
    with pytest.raises(ValidationError, match="no se pueden eliminar"):
        evento.delete()


@pytest.mark.django_db
def test_evento_conserva_etiqueta_si_el_actor_se_desactiva():
    actor = get_user_model().objects.create_user(
        username="operadora",
        password="secreto123",
        first_name="Romina",
        last_name="Hernández",
    )
    evento = registrar_evento(
        actor=actor,
        accion=EventoAuditoria.ACCION_MODIFICAR,
        entidad="asociados.Asociado",
        objeto_id="2",
        objeto_descripcion="López, Mara",
        cambios={"telefono": {"anterior": "123", "nuevo": "456"}},
        origen=EventoAuditoria.ORIGEN_GESTION,
    )

    actor.is_active = False
    actor.save(update_fields=["is_active"])
    evento.refresh_from_db()

    assert evento.actor_etiqueta == "Romina Hernández"


@pytest.mark.django_db
def test_evento_usa_username_si_el_actor_no_tiene_nombre_completo():
    actor = get_user_model().objects.create_user(username="operadora", password="secreto123")

    evento = registrar_evento(
        actor=actor,
        accion=EventoAuditoria.ACCION_MODIFICAR,
        entidad="asociados.Asociado",
        objeto_id="3",
        objeto_descripcion="Pérez, Ana",
        cambios={},
        origen=EventoAuditoria.ORIGEN_GESTION,
    )

    assert evento.actor_etiqueta == "operadora"


@pytest.mark.django_db
def test_serializacion_de_evento_no_incluye_contrasenas():
    actor = get_user_model().objects.create_user(username="seguridad", password="secreto123")
    evento = registrar_evento(
        actor=actor,
        accion=EventoAuditoria.ACCION_MODIFICAR,
        entidad="auth.User",
        objeto_id=actor.pk,
        objeto_descripcion=actor.username,
        cambios={"is_active": {"anterior": True, "nuevo": False}},
        origen=EventoAuditoria.ORIGEN_ADMIN,
    )

    assert "password" not in evento.cambios
    assert "secreto123" not in str(evento.cambios)


@pytest.mark.django_db
def test_anulacion_requiere_motivo():
    actor = get_user_model().objects.create_user(username="tesorera", password="secreto123")

    with pytest.raises(ValidationError, match="requiere un motivo"):
        registrar_evento(
            actor=actor,
            accion=EventoAuditoria.ACCION_ANULAR,
            entidad="cuotas.Pago",
            objeto_id="1",
            objeto_descripcion="Pago 1",
            cambios={},
            origen=EventoAuditoria.ORIGEN_GESTION,
        )
