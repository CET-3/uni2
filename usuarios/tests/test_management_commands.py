from datetime import timedelta
from io import StringIO

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.sessions.models import Session
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings
from django.utils import timezone

from asociados.models import Asociado
from comercios.models import ActividadComercial, Comercio
from config.database_identity import database_fingerprint, database_role_fingerprint
from contenidos.models import CategoriaProductoServicio, ProductoServicio
from gestion.permissions import GESTION_COBRAR_CUOTAS, GESTION_IMPORTAR_ASOCIADOS, GESTION_VER_DESIGN_SYSTEM
from usuarios.models import EstadoDatosStaging
from usuarios.services import ASOCIADO_GROUP, COMERCIO_GROUP


SERVICIOS_VERCEL = {"Fotocopias", "Uniformes", "Bicicleta solidaria", "Cuadernillos y anillado"}
RUBROS_VERCEL = {"Gastronomía", "Actividad física", "Belleza", "Vestimenta", "Educación", "Tecnología y accesorios"}
COMERCIOS_VERCEL = {"Alto Drugstore", "Librería Muñoz", "Atenas Gimnasio", "Andromeda Studio", "Carolina's Closet", "Techno Store"}


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


def test_huella_base_no_expone_la_contrasena_configurada():
    output = StringIO()

    call_command("huella_base", stdout=output)

    assert output.getvalue().strip() == database_fingerprint(settings.DATABASES["default"])


def test_huella_base_puede_calcular_la_identidad_separada_del_rol():
    output = StringIO()

    call_command("huella_base", rol=True, stdout=output)

    assert output.getvalue().strip() == database_role_fingerprint(
        settings.DATABASES["default"]
    )


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


@pytest.mark.django_db
@override_settings(
    UNI2_ALLOW_STAGING_COMMAND_ON_SQLITE=True,
    UNI2_DEPLOYMENT_ENVIRONMENT="staging",
    UNI2_STAGING_DATABASE_LABEL="uni2-staging",
    PWA_PRIVATE_DATA_EPOCH="2026-08-02-01",
)
def test_preparar_copia_staging_invalida_accesos_y_crea_usuarios_qa(monkeypatch):
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
    asociado.usuario = old_user
    asociado.save(update_fields=["usuario"])
    Session.objects.create(
        session_key="sesion-productiva",
        session_data="dato",
        expire_date=timezone.now() + timedelta(days=1),
    )
    set_staging_qa_credentials(monkeypatch)

    call_command(
        "preparar_copia_staging",
        refresh_id="2026-08-02-01",
        confirm_target="uni2-staging",
    )

    old_user.refresh_from_db()
    asociado.refresh_from_db()
    qa_admin = get_user_model().objects.get(username="qa-admin")
    qa_asociado_a = get_user_model().objects.get(username="qa-asociado-a")
    qa_asociado_b = get_user_model().objects.get(username="qa-asociado-b")
    qa_comercio = get_user_model().objects.get(username="qa-comercio")
    assert not Session.objects.exists()
    assert not old_user.is_active
    assert not old_user.is_staff
    assert not old_user.is_superuser
    assert not old_user.has_usable_password()
    assert asociado.token_credencial != old_token
    assert asociado.usuario == old_user
    assert qa_admin.is_active and qa_admin.is_staff and qa_admin.is_superuser
    assert qa_admin.check_password("clave-qa-admin-segura")
    assert qa_asociado_a.asociado.dni == "QA-STAGING-A"
    assert qa_asociado_b.asociado.dni == "QA-STAGING-B"
    assert qa_asociado_a.check_password("clave-qa-asociado-a-segura")
    assert qa_asociado_b.check_password("clave-qa-asociado-b-segura")
    assert qa_asociado_a.groups.filter(name=ASOCIADO_GROUP).exists()
    assert qa_asociado_b.groups.filter(name=ASOCIADO_GROUP).exists()
    assert qa_comercio.comercio.nombre == "Comercio QA Staging"
    assert qa_comercio.comercio.estado == Comercio.ESTADO_FIRMADO
    assert qa_comercio.check_password("clave-qa-comercio-segura")
    assert qa_comercio.groups.filter(name=COMERCIO_GROUP).exists()
    assert get_user_model().objects.filter(is_active=True).count() == 4
    assert EstadoDatosStaging.objects.get().refresh_id == "2026-08-02-01"


@pytest.mark.django_db
@override_settings(
    UNI2_ALLOW_STAGING_COMMAND_ON_SQLITE=True,
    UNI2_DEPLOYMENT_ENVIRONMENT="staging",
    UNI2_STAGING_DATABASE_LABEL="uni2-staging",
    PWA_PRIVATE_DATA_EPOCH="2026-08-02-01",
)
def test_preparar_copia_staging_aborta_antes_de_tocar_un_destino_no_confirmado(monkeypatch):
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
def test_preparar_copia_staging_revierte_todo_si_falla_despues_de_invalidar(monkeypatch):
    asociado = Asociado.objects.create(
        nombre="Rita",
        apellido="Rollback",
        dni="40999888",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta="2026-01-01",
        fecha_inicio_cobro="2026-01-01",
    )
    old_token = asociado.token_credencial
    user = get_user_model().objects.create_user(
        username="usuario-productivo",
        password="sigue-intacto",
    )
    Session.objects.create(
        session_key="sesion-productiva",
        session_data="dato",
        expire_date=timezone.now() + timedelta(days=1),
    )
    set_staging_qa_credentials(monkeypatch)

    def fail_after_creating_qa_users(**kwargs):
        raise RuntimeError("fallo inducido después de invalidar")

    monkeypatch.setattr(
        "usuarios.staging._create_qa_comercio",
        fail_after_creating_qa_users,
    )

    with pytest.raises(CommandError, match="transacción fue revertida"):
        call_command(
            "preparar_copia_staging",
            refresh_id="2026-08-02-01",
            confirm_target="uni2-staging",
        )

    user.refresh_from_db()
    asociado.refresh_from_db()
    assert user.is_active
    assert user.check_password("sigue-intacto")
    assert asociado.token_credencial == old_token
    assert Session.objects.filter(session_key="sesion-productiva").exists()
    assert not EstadoDatosStaging.objects.exists()
    assert not get_user_model().objects.filter(username__startswith="qa-").exists()
