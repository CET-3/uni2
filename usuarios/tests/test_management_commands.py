from datetime import timedelta
from io import StringIO

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings
from django.utils import timezone

from asociados.models import Asociado
from comercios.models import ActividadComercial, Comercio
from config.database_identity import database_fingerprint, database_role_fingerprint
from contenidos.models import CategoriaProductoServicio, ProductoServicio
from gestion.permissions import (
    GESTION_COBRAR_CUOTAS,
    GESTION_IMPORTAR_ASOCIADOS,
    GESTION_VER_AUDITORIA,
    GESTION_VER_DESIGN_SYSTEM,
    GESTION_VER_MOVIMIENTOS_ASOCIADO,
)
from usuarios.models import EstadoDatosStaging
from usuarios.roles import (
    ADMINISTRADOR_APP_GROUP,
    ATENCION_ASOCIADO_GROUP,
    EQUIPO_PROYECTO_GROUP,
    GESTION_PUBLICIDADES_GROUP,
)
from usuarios.services import ASOCIADO_GROUP, COMERCIO_GROUP
from usuarios.management.commands import preflight_staging_deploy

SERVICIOS_VERCEL = {
    "Fotocopias",
    "Uniformes",
    "Bicicleta solidaria",
    "Cuadernillos y anillado",
}
RUBROS_VERCEL = {
    "Gastronomía",
    "Actividad física",
    "Belleza",
    "Vestimenta",
    "Educación",
    "Tecnología y accesorios",
}
COMERCIOS_VERCEL = {
    "Alto Drugstore",
    "Librería Muñoz",
    "Atenas Gimnasio",
    "Andromeda Studio",
    "Carolina's Closet",
    "Techno Store",
}


def set_staging_qa_credentials(monkeypatch):
    credentials = {
        "UNI2_STAGING_QA_ADMIN_USERNAME": "qa-admin",
        "UNI2_STAGING_QA_ADMIN_PASSWORD": "clave-qa-admin-segura",
        "UNI2_STAGING_QA_ASOCIADO_A_USERNAME": "qa-asociado-a",
        "UNI2_STAGING_QA_ASOCIADO_A_PASSWORD": "clave-qa-asociado-a-segura",
        "UNI2_STAGING_QA_ASOCIADO_B_USERNAME": "qa-asociado-b",
        "UNI2_STAGING_QA_ASOCIADO_B_PASSWORD": "clave-qa-asociado-b-segura",
        "UNI2_STAGING_QA_COMERCIO_USERNAME": "qa-comercio",
        "UNI2_STAGING_QA_COMERCIO_PASSWORD": "clave-qa-comercio-segura",
    }
    for name, value in credentials.items():
        monkeypatch.setenv(name, value)


def _staging_preflight_settings():
    return {
        "DJANGO_SETTINGS_MODULE": "config.settings.staging",
        "UNI2_ENVIRONMENT": "staging",
        "UNI2_DEPLOYMENT_ENVIRONMENT": "staging",
        "DATABASES": {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": "postgres",
                "HOST": "staging.example",
                "PORT": "5432",
                "USER": "staging",
            }
        },
    }


def _set_staging_preflight_environment(monkeypatch):
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "config.settings.staging")
    monkeypatch.setenv("UNI2_ENVIRONMENT", "staging")
    for name in preflight_staging_deploy.REQUIRED_ENVIRONMENT[2:]:
        monkeypatch.setenv(name, "a" * 64 if "FINGERPRINT" in name else "configured")


@override_settings(**_staging_preflight_settings())
def test_preflight_staging_aprueba_plan_de_migraciones_exacto(monkeypatch):
    _set_staging_preflight_environment(monkeypatch)
    monkeypatch.setattr(
        preflight_staging_deploy,
        "pending_migrations",
        lambda: ["asociados.0011_solicitudasociacion_clave_operacion"],
    )
    output = StringIO()

    call_command(
        "preflight_staging_deploy",
        expected_migration=[
            "asociados.0011_solicitudasociacion_clave_operacion"
        ],
        stdout=output,
    )

    assert "Preflight staging aprobado" in output.getvalue()
    assert "Migraciones pendientes: 1" in output.getvalue()


@override_settings(**_staging_preflight_settings())
def test_preflight_staging_rechaza_plan_distinto(monkeypatch):
    _set_staging_preflight_environment(monkeypatch)
    monkeypatch.setattr(
        preflight_staging_deploy,
        "pending_migrations",
        lambda: ["cuotas.0006_pago_clave_operacion"],
    )

    with pytest.raises(CommandError, match="plan de migraciones no coincide"):
        call_command(
            "preflight_staging_deploy",
            expected_migration=[
                "asociados.0011_solicitudasociacion_clave_operacion"
            ],
        )


@override_settings(**_staging_preflight_settings())
def test_preflight_staging_rechaza_entorno_que_no_es_staging(monkeypatch):
    _set_staging_preflight_environment(monkeypatch)
    monkeypatch.setenv("UNI2_ENVIRONMENT", "production")

    with pytest.raises(CommandError, match="UNI2_ENVIRONMENT=staging"):
        call_command("preflight_staging_deploy")


def test_huella_base_no_expone_la_contrasena_configurada():
    output = StringIO()

    call_command("huella_base", stdout=output)

    assert output.getvalue().strip() == database_fingerprint(
        settings.DATABASES["default"]
    )


def test_huella_base_puede_calcular_la_identidad_separada_del_rol():
    output = StringIO()

    call_command("huella_base", rol=True, stdout=output)

    assert output.getvalue().strip() == database_role_fingerprint(
        settings.DATABASES["default"]
    )


def test_huella_base_distingue_proyectos_en_un_pooler_compartido():
    common_connection = {
        "HOST": "aws-0-sa-east-1.pooler.supabase.com",
        "PORT": "6543",
        "NAME": "postgres",
    }

    production_fingerprint = database_fingerprint(
        {**common_connection, "USER": "postgres.production-ref"}
    )
    staging_fingerprint = database_fingerprint(
        {**common_connection, "USER": "postgres.staging-ref"}
    )

    assert production_fingerprint != staging_fingerprint


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

    assert admin.groups.filter(name=ADMINISTRADOR_APP_GROUP).exists()
    assert atencion_user.groups.filter(name=ATENCION_ASOCIADO_GROUP).exists()
    assert atencion_user.groups.filter(name="Asociados").exists()
    assert atencion_user.has_perm(GESTION_COBRAR_CUOTAS)
    assert not atencion_user.has_perm(GESTION_VER_DESIGN_SYSTEM)
    assert admin.has_perm(GESTION_VER_DESIGN_SYSTEM)
    assert admin.has_perm(GESTION_VER_AUDITORIA)
    assert not atencion_user.has_perm(GESTION_IMPORTAR_ASOCIADOS)
    assert not atencion_user.has_perm(GESTION_VER_AUDITORIA)
    assert atencion_user.has_perm(GESTION_VER_MOVIMIENTOS_ASOCIADO)
    assert asociado_user.groups.filter(name="Asociados").exists()
    assert comercio_user.groups.filter(name="Comercios").exists()
    assert Group.objects.filter(name=ATENCION_ASOCIADO_GROUP).exists()
    assert Asociado.objects.get(dni="40111223").usuario == atencion_user
    assert Asociado.objects.get(dni="40111222").usuario == asociado_user
    assert Comercio.objects.get(nombre="Librería Sur").usuario == comercio_user


@pytest.mark.django_db
def test_sincronizar_grupos_informa_aplica_y_es_idempotente():
    equipo = Group.objects.get(name=EQUIPO_PROYECTO_GROUP)
    permiso_extra = Permission.objects.get(
        content_type__app_label="auth", codename="delete_user"
    )
    equipo.permissions.add(permiso_extra)
    publicidades = Group.objects.get(name=GESTION_PUBLICIDADES_GROUP)
    publicidades_user = get_user_model().objects.create_user(
        username="publicidades-con-matriz-desviada", is_staff=True
    )
    publicidades_user.groups.add(publicidades)
    publicidades.permissions.clear()
    output = StringIO()

    call_command("sincronizar_grupos", stdout=output)

    assert "Ejecutá nuevamente con --apply" in output.getvalue()
    with pytest.raises(CommandError, match="no está sincronizada"):
        call_command("sincronizar_grupos", check=True)

    call_command("sincronizar_grupos", apply=True)
    output = StringIO()
    call_command("sincronizar_grupos", check=True, stdout=output)

    assert "está sincronizada" in output.getvalue()
    assert not equipo.permissions.filter(pk=permiso_extra.pk).exists()
    publicidades_user.refresh_from_db()
    assert publicidades_user.is_staff


@pytest.mark.django_db
def test_limpiar_permisos_huerfanos_informa_sin_borrar_por_defecto():
    content_type = ContentType.objects.create(
        app_label="legado", model="modelo_eliminado"
    )
    permiso = Permission.objects.create(
        content_type=content_type,
        codename="view_modeloeliminado",
        name="Can view modelo eliminado",
    )
    grupo = Group.objects.create(name="Marketing legado")
    grupo.permissions.add(permiso)
    usuario = get_user_model().objects.create_user(username="legado")
    usuario.user_permissions.add(permiso)

    output = StringIO()
    call_command("limpiar_permisos_huerfanos", stdout=output)

    assert "legado.modelo_eliminado" in output.getvalue()
    assert Permission.objects.filter(pk=permiso.pk).exists()
    assert ContentType.objects.filter(pk=content_type.pk).exists()


@pytest.mark.django_db
def test_limpiar_permisos_huerfanos_apply_borra_permisos_y_content_type():
    content_type = ContentType.objects.create(
        app_label="legado", model="modelo_eliminado"
    )
    permiso = Permission.objects.create(
        content_type=content_type,
        codename="view_modeloeliminado",
        name="Can view modelo eliminado",
    )

    call_command("limpiar_permisos_huerfanos", apply=True)

    assert not Permission.objects.filter(pk=permiso.pk).exists()
    assert not ContentType.objects.filter(pk=content_type.pk).exists()


@pytest.mark.django_db
def test_limpiar_permisos_huerfanos_check_falla_y_preserva_custom_historico():
    content_type = ContentType.objects.get(
        app_label="contenidos", model="publicidad"
    )
    permiso = Permission.objects.create(
        content_type=content_type,
        codename="permiso_historico",
        name="Permiso histórico",
    )
    output = StringIO()

    with pytest.raises(CommandError, match="permisos huérfanos"):
        call_command("limpiar_permisos_huerfanos", check=True, stdout=output)

    assert "no se elimina automáticamente" in output.getvalue()
    call_command("limpiar_permisos_huerfanos", apply=True)
    assert Permission.objects.filter(pk=permiso.pk).exists()
    output = StringIO()
    call_command("limpiar_permisos_huerfanos", stdout=output)
    assert "permiso_historico" in output.getvalue()


@pytest.mark.django_db
def test_carga_inicial_crea_servicios_vercel():
    call_command("carga_inicial")
    nombres = set(CategoriaProductoServicio.objects.values_list("nombre", flat=True))
    assert SERVICIOS_VERCEL.issubset(nombres), (
        f"Faltan servicios: {SERVICIOS_VERCEL - nombres}"
    )
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
    assert COMERCIOS_VERCEL.issubset(nombres), (
        f"Faltan comercios: {COMERCIOS_VERCEL - nombres}"
    )


@pytest.mark.django_db
@override_settings(
    UNI2_ALLOW_STAGING_COMMAND_ON_SQLITE=True,
    UNI2_DEPLOYMENT_ENVIRONMENT="staging",
    UNI2_STAGING_DATABASE_LABEL="uni2-staging",
    PWA_PRIVATE_DATA_EPOCH="2026-08-02-01",
)
def test_preparar_copia_staging_conserva_usuarios_y_elimina_sesiones(monkeypatch):
    asociado = Asociado.objects.create(
        nombre="Ana",
        apellido="Producción",
        dni="40123456",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta="2026-01-01",
        fecha_inicio_cobro="2026-01-01",
    )
    old_token = asociado.token_credencial
    old_user = get_user_model().objects.create_superuser(
        username="admin-produccion",
        password="clave-productiva",
    )
    grupo = Group.objects.create(name="grupo-personalizado")
    old_user.groups.add(grupo)
    permiso = Permission.objects.get(
        content_type__app_label="gestion",
        codename=GESTION_COBRAR_CUOTAS.split(".", 1)[1],
    )
    old_user.user_permissions.add(permiso)
    asociado.usuario = old_user
    asociado.save(update_fields=["usuario"])
    actividad = ActividadComercial.objects.create(nombre="Librería")
    Comercio.objects.create(
        nombre="Comercio de Ana",
        actividad_comercial=actividad,
        usuario=old_user,
    )
    old_password_hash = old_user.password
    old_is_active = old_user.is_active
    old_is_staff = old_user.is_staff
    old_is_superuser = old_user.is_superuser
    old_groups = list(old_user.groups.values_list("name", flat=True))
    old_permissions = list(old_user.user_permissions.values_list("pk", flat=True))
    Session.objects.create(
        session_key="sesion-productiva",
        session_data="dato",
        expire_date=timezone.now() + timedelta(days=1),
    )
    for name in (
        "UNI2_STAGING_QA_ADMIN_USERNAME",
        "UNI2_STAGING_QA_ADMIN_PASSWORD",
        "UNI2_STAGING_QA_ASOCIADO_A_USERNAME",
        "UNI2_STAGING_QA_ASOCIADO_A_PASSWORD",
        "UNI2_STAGING_QA_ASOCIADO_B_USERNAME",
        "UNI2_STAGING_QA_ASOCIADO_B_PASSWORD",
        "UNI2_STAGING_QA_COMERCIO_USERNAME",
        "UNI2_STAGING_QA_COMERCIO_PASSWORD",
    ):
        monkeypatch.delenv(name, raising=False)

    output = StringIO()
    call_command(
        "preparar_copia_staging",
        refresh_id="2026-08-02-01",
        confirm_target="uni2-staging",
        stdout=output,
    )

    old_user.refresh_from_db()
    asociado.refresh_from_db()
    comercio = Comercio.objects.get(nombre="Comercio de Ana")
    assert get_user_model().objects.count() == 1
    assert old_user.password == old_password_hash
    assert old_user.is_active == old_is_active
    assert old_user.is_staff == old_is_staff
    assert old_user.is_superuser == old_is_superuser
    assert list(old_user.groups.values_list("name", flat=True)) == old_groups
    assert list(old_user.user_permissions.values_list("pk", flat=True)) == old_permissions
    assert asociado.usuario_id == old_user.pk
    assert comercio.usuario_id == old_user.pk
    assert not Session.objects.exists()
    assert asociado.token_credencial == old_token
    assert EstadoDatosStaging.objects.get().refresh_id == "2026-08-02-01"
    assert "1 sesiones eliminadas" in output.getvalue()
    assert "1 usuarios conservados" in output.getvalue()
    assert "QA" not in output.getvalue()


@pytest.mark.django_db
@override_settings(
    UNI2_ALLOW_STAGING_COMMAND_ON_SQLITE=True,
    UNI2_DEPLOYMENT_ENVIRONMENT="staging",
    UNI2_STAGING_DATABASE_LABEL="uni2-staging",
    PWA_PRIVATE_DATA_EPOCH="2026-08-02-01",
)
def test_preparar_copia_staging_aborta_antes_de_tocar_un_destino_no_confirmado(
    monkeypatch,
):
    user = get_user_model().objects.create_user(
        username="usuario-productivo",
        password="sigue-intacto",
    )
    set_staging_qa_credentials(monkeypatch)

    with pytest.raises(CommandError, match="confirmación no coincide"):
        call_command(
            "preparar_copia_staging",
            refresh_id="2026-08-02-01",
            confirm_target="otra-base",
        )

    user.refresh_from_db()
    assert user.is_active
    assert user.check_password("sigue-intacto")


@pytest.mark.django_db(transaction=True)
@override_settings(
    UNI2_ALLOW_STAGING_COMMAND_ON_SQLITE=True,
    UNI2_DEPLOYMENT_ENVIRONMENT="staging",
    UNI2_STAGING_DATABASE_LABEL="uni2-staging",
    PWA_PRIVATE_DATA_EPOCH="2026-08-02-01",
)
def test_preparar_copia_staging_revierte_sesiones_si_falla_el_marcador(
    monkeypatch,
):
    asociado = Asociado.objects.create(
        nombre="Rita",
        apellido="Rollback",
        dni="40999888",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta="2026-01-01",
        fecha_inicio_cobro="2026-01-01",
    )
    user = get_user_model().objects.create_user(
        username="usuario-productivo",
        password="sigue-intacto",
    )
    Session.objects.create(
        session_key="sesion-productiva",
        session_data="dato",
        expire_date=timezone.now() + timedelta(days=1),
    )

    def fail_writing_staging_marker(**kwargs):
        raise RuntimeError("fallo inducido al escribir el marcador")

    monkeypatch.setattr(
        EstadoDatosStaging.objects,
        "update_or_create",
        fail_writing_staging_marker,
    )

    with pytest.raises(CommandError, match="transacción fue revertida"):
        call_command(
            "preparar_copia_staging",
            refresh_id="2026-08-02-01",
            confirm_target="uni2-staging",
        )

    user.refresh_from_db()
    assert user.is_active
    assert user.check_password("sigue-intacto")
    assert Session.objects.filter(session_key="sesion-productiva").exists()
    assert not EstadoDatosStaging.objects.exists()


@pytest.mark.django_db
@override_settings(
    UNI2_ALLOW_STAGING_COMMAND_ON_SQLITE=True,
    UNI2_DEPLOYMENT_ENVIRONMENT="staging",
    UNI2_STAGING_DATABASE_LABEL="uni2-staging",
    PWA_PRIVATE_DATA_EPOCH="2026-08-02-01",
)
def test_rotar_contraseñas_qa_staging_actualiza_solo_las_cuentas_qa(monkeypatch):
    user_model = get_user_model()
    qa_admin = user_model.objects.create_superuser(
        username="qa-admin",
        password="clave-admin-anterior",
    )
    asociado_group, _ = Group.objects.get_or_create(name=ASOCIADO_GROUP)
    comercio_group, _ = Group.objects.get_or_create(name=COMERCIO_GROUP)
    qa_asociado_a_user = user_model.objects.create_user(
        username="qa-asociado-a",
        password="clave-asociado-a-anterior",
    )
    qa_asociado_a_user.groups.add(asociado_group)
    Asociado.objects.create(
        usuario=qa_asociado_a_user,
        nombre="Asociado",
        apellido="QA A",
        dni="QA-STAGING-A",
        tipo=Asociado.TIPO_ASOCIADO,
        estado=Asociado.ESTADO_ACTIVO,
        fecha_alta="2026-01-01",
        fecha_inicio_cobro="2026-01-01",
    )
    qa_asociado_b_user = user_model.objects.create_user(
        username="qa-asociado-b",
        password="clave-asociado-b-anterior",
    )
    qa_asociado_b_user.groups.add(asociado_group)
    Asociado.objects.create(
        usuario=qa_asociado_b_user,
        nombre="Asociado",
        apellido="QA B",
        dni="QA-STAGING-B",
        tipo=Asociado.TIPO_ASOCIADO,
        estado=Asociado.ESTADO_ACTIVO,
        fecha_alta="2026-01-01",
        fecha_inicio_cobro="2026-01-01",
    )
    actividad = ActividadComercial.objects.create(nombre="Pruebas internas")
    qa_comercio = user_model.objects.create_user(
        username="qa-comercio",
        password="clave-comercio-anterior",
    )
    qa_comercio.groups.add(comercio_group)
    Comercio.objects.create(
        actividad_comercial=actividad,
        usuario=qa_comercio,
        nombre="Comercio QA Staging",
        estado=Comercio.ESTADO_FIRMADO,
    )
    usuario_fuera_de_qa = user_model.objects.create_user(
        username="usuario-fuera-de-qa",
        password="clave-fuera-de-qa-anterior",
    )
    set_staging_qa_credentials(monkeypatch)

    nuevas = {
        "UNI2_STAGING_QA_ADMIN_PASSWORD": "una-clave-admin-mas-amigable",
        "UNI2_STAGING_QA_ASOCIADO_A_PASSWORD": "una-clave-asociado-a-amigable",
        "UNI2_STAGING_QA_ASOCIADO_B_PASSWORD": "una-clave-asociado-b-amigable",
        "UNI2_STAGING_QA_COMERCIO_PASSWORD": "una-clave-comercio-amigable",
    }
    for name, value in nuevas.items():
        monkeypatch.setenv(name, value)

    call_command("rotar_passwords_qa_staging")

    assert user_model.objects.get(username="qa-admin").check_password(
        nuevas["UNI2_STAGING_QA_ADMIN_PASSWORD"]
    )
    assert user_model.objects.get(username="qa-asociado-a").check_password(
        nuevas["UNI2_STAGING_QA_ASOCIADO_A_PASSWORD"]
    )
    assert user_model.objects.get(username="qa-asociado-b").check_password(
        nuevas["UNI2_STAGING_QA_ASOCIADO_B_PASSWORD"]
    )
    assert user_model.objects.get(username="qa-comercio").check_password(
        nuevas["UNI2_STAGING_QA_COMERCIO_PASSWORD"]
    )
    assert usuario_fuera_de_qa.check_password("clave-fuera-de-qa-anterior")
