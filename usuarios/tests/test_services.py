import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import IntegrityError

from asociados.models import Asociado
from asociados.services import create_asociado
from comercios.models import Comercio
from usuarios.services import (
    ASOCIADO_GROUP,
    COMERCIO_GROUP,
    create_missing_users_for_asociados,
    create_user_for_asociado,
    create_user_for_comercio,
    ensure_default_groups,
    get_available_experiences,
    sincronizar_acceso_admin,
)
from usuarios.roles import (
    ACCESO_ADMIN_TECNICO,
    ATENCION_ASOCIADO_GROUP,
    GESTION_CONVENIOS_GROUP,
)


@pytest.mark.django_db
def test_grupo_convenios_activa_y_desactiva_acceso_admin():
    usuario = get_user_model().objects.create_user(username="convenios")
    grupo = Group.objects.get(name=GESTION_CONVENIOS_GROUP)

    usuario.groups.add(grupo)
    sincronizar_acceso_admin(usuario)
    assert usuario.is_staff
    assert "gestion" in get_available_experiences(usuario)

    usuario.groups.remove(grupo)
    sincronizar_acceso_admin(usuario)
    assert not usuario.is_staff


@pytest.mark.django_db
def test_atencion_al_asociado_no_activa_acceso_admin():
    usuario = get_user_model().objects.create_user(username="atencion_sin_admin")
    usuario.groups.add(Group.objects.get(name=ATENCION_ASOCIADO_GROUP))

    sincronizar_acceso_admin(usuario)

    assert not usuario.is_staff


@pytest.mark.django_db
def test_grupo_nuevo_activa_admin_por_capacidad_y_no_por_nombre():
    usuario = get_user_model().objects.create_user(username="rol_futuro")
    grupo = Group.objects.create(name="Rol creado en el futuro")
    app_label, codename = ACCESO_ADMIN_TECNICO.split(".", 1)
    permiso = grupo.permissions.model.objects.get(
        content_type__app_label=app_label,
        codename=codename,
    )
    grupo.permissions.add(permiso)
    usuario.groups.add(grupo)

    sincronizar_acceso_admin(usuario)

    assert usuario.is_staff


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
def test_create_missing_users_for_asociados_crea_usuarios_faltantes_y_es_idempotente():
    ensure_default_groups()
    asociado = Asociado.objects.create(
        nombre="Lena",
        apellido="Leyes",
        dni="52328996",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta="2026-03-01",
        fecha_inicio_cobro="2026-03-01",
    )

    resultado = create_missing_users_for_asociados()
    segundo_resultado = create_missing_users_for_asociados()

    asociado.refresh_from_db()
    assert resultado.creados == 1
    assert resultado.omitidos == 0
    assert resultado.errores == []
    assert asociado.usuario is not None
    assert asociado.usuario.username == "52328996"
    assert asociado.usuario.check_password("52328996")
    assert Group.objects.get(name=ASOCIADO_GROUP) in asociado.usuario.groups.all()
    assert segundo_resultado.creados == 0
    assert segundo_resultado.omitidos == 1
    assert segundo_resultado.errores == []


@pytest.mark.django_db
def test_create_missing_users_for_asociados_en_lotes():
    ensure_default_groups()
    primero = Asociado.objects.create(
        nombre="Lena",
        apellido="Leyes",
        dni="52328996",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta="2026-03-01",
        fecha_inicio_cobro="2026-03-01",
    )
    segundo = Asociado.objects.create(
        nombre="Joaquin",
        apellido="Darosa",
        dni="52536191",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta="2026-03-01",
        fecha_inicio_cobro="2026-03-01",
    )

    resultado_1 = create_missing_users_for_asociados(batch_size=1)
    resultado_2 = create_missing_users_for_asociados(batch_size=1, after_id=resultado_1.siguiente_cursor)

    primero.refresh_from_db()
    segundo.refresh_from_db()
    assert resultado_1.procesados == 1
    assert resultado_1.hay_mas is True
    assert resultado_1.restantes == 1
    assert resultado_1.siguiente_cursor == primero.id
    assert resultado_2.procesados == 1
    assert resultado_2.hay_mas is False
    assert resultado_2.restantes == 0
    assert primero.usuario is not None
    assert segundo.usuario is not None


@pytest.mark.django_db
def test_create_missing_users_for_asociados_reconoce_race_con_usuario_creado_en_otro_proceso(monkeypatch):
    ensure_default_groups()
    user_model = get_user_model()
    asociado = Asociado.objects.create(
        nombre="Lena",
        apellido="Leyes",
        dni="53015244",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta="2026-03-01",
        fecha_inicio_cobro="2026-03-01",
    )

    def crear_usuario_interferente(*, asociado, password, email=None):
        user = user_model.objects.create_user(
            username=str(asociado.dni),
            password=password,
            email=email or asociado.email,
            first_name=asociado.nombre,
            last_name=asociado.apellido,
            is_active=True,
        )
        raise IntegrityError("duplicate key value violates unique constraint")

    monkeypatch.setattr("usuarios.services.create_user_for_asociado", crear_usuario_interferente)

    resultado = create_missing_users_for_asociados()

    asociado.refresh_from_db()
    assert resultado.creados == 0
    assert resultado.vinculados == 1
    assert resultado.errores == []
    assert asociado.usuario is not None
    assert asociado.usuario.username == "53015244"


@pytest.mark.django_db
def test_create_missing_users_for_asociados_vincula_usuario_existente_sin_asociado():
    ensure_default_groups()
    user_model = get_user_model()
    user_existente = user_model.objects.create_user(username="52328996", password="existente")
    asociado = Asociado.objects.create(
        nombre="Lena",
        apellido="Leyes",
        dni="52328996",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta="2026-03-01",
        fecha_inicio_cobro="2026-03-01",
    )
    resultado = create_missing_users_for_asociados()

    asociado.refresh_from_db()
    user_existente.refresh_from_db()
    assert resultado.creados == 0
    assert resultado.vinculados == 1
    assert resultado.omitidos == 0
    assert resultado.errores == []
    assert asociado.usuario == user_existente
    assert Group.objects.get(name=ASOCIADO_GROUP) in user_existente.groups.all()


@pytest.mark.django_db
def test_create_missing_users_for_asociados_continua_si_username_pertenece_a_otro_asociado():
    ensure_default_groups()
    user_model = get_user_model()
    user_existente = user_model.objects.create_user(username="52328996", password="existente")
    Asociado.objects.create(
        nombre="Otra",
        apellido="Persona",
        dni="30000000",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta="2026-03-01",
        fecha_inicio_cobro="2026-03-01",
        usuario=user_existente,
    )
    asociado_con_conflicto = Asociado.objects.create(
        nombre="Lena",
        apellido="Leyes",
        dni="52328996",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta="2026-03-01",
        fecha_inicio_cobro="2026-03-01",
    )

    resultado = create_missing_users_for_asociados()

    asociado_con_conflicto.refresh_from_db()
    assert resultado.creados == 0
    assert resultado.vinculados == 0
    assert resultado.omitidos == 1
    assert len(resultado.errores) == 1
    assert "52328996" in resultado.errores[0]
    assert asociado_con_conflicto.usuario is None


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
