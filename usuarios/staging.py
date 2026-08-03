import uuid
from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password
from django.contrib.sessions.models import Session
from django.db import transaction
from django.utils import timezone

from asociados.models import Asociado
from comercios.models import ActividadComercial, Comercio

from .models import EstadoDatosStaging
from .services import ASOCIADO_GROUP, COMERCIO_GROUP, ensure_default_groups


@dataclass(frozen=True)
class StagingHardeningResult:
    sesiones_eliminadas: int
    usuarios_invalidados: int
    tokens_regenerados: int
    usuarios_qa_creados: int


QA_ASOCIADOS = (
    {
        "nombre": "Asociado",
        "apellido": "QA A",
        "dni": "QA-STAGING-A",
    },
    {
        "nombre": "Asociado",
        "apellido": "QA B",
        "dni": "QA-STAGING-B",
    },
)
QA_COMERCIO_NAME = "Comercio QA Staging"


def _new_credential_tokens(count, forbidden_tokens):
    tokens = []
    used = set(forbidden_tokens)
    while len(tokens) < count:
        candidate = uuid.uuid4()
        if candidate in used:
            continue
        used.add(candidate)
        tokens.append(candidate)
    return tokens


def _create_qa_asociado(*, user_model, group, credentials, identity):
    user = user_model.objects.create_user(
        username=credentials["username"],
        email="",
        password=credentials["password"],
        first_name=identity["nombre"],
        last_name=identity["apellido"],
        is_active=True,
    )
    user.groups.add(group)
    Asociado.objects.create(
        usuario=user,
        nombre=identity["nombre"],
        apellido=identity["apellido"],
        dni=identity["dni"],
        tipo=Asociado.TIPO_ASOCIADO,
        estado=Asociado.ESTADO_ACTIVO,
        fecha_alta=timezone.localdate(),
        fecha_inicio_cobro=timezone.localdate(),
    )


def _create_qa_comercio(*, user_model, group, credentials):
    user = user_model.objects.create_user(
        username=credentials["username"],
        email="",
        password=credentials["password"],
        first_name=QA_COMERCIO_NAME,
        is_active=True,
    )
    user.groups.add(group)
    activity, _ = ActividadComercial.objects.get_or_create(
        nombre="Pruebas internas de staging",
        defaults={
            "descripcion": "Rubro ficticio exclusivo para la validación de staging.",
        },
    )
    Comercio.objects.create(
        actividad_comercial=activity,
        usuario=user,
        nombre=QA_COMERCIO_NAME,
        descripcion="Comercio ficticio exclusivo del entorno de staging.",
        propietario="Datos ficticios",
        beneficio_texto="Validación interna sin beneficio comercial.",
        estado=Comercio.ESTADO_FIRMADO,
    )


@transaction.atomic
def harden_staging_clone(
    *,
    qa_admin_username,
    qa_admin_password,
    refresh_id,
    qa_asociado_a_username,
    qa_asociado_a_password,
    qa_asociado_b_username,
    qa_asociado_b_password,
    qa_comercio_username,
    qa_comercio_password,
):
    """Invalida autenticación productiva y crea accesos exclusivos de QA."""

    user_model = get_user_model()
    qa_credentials = (
        {"username": qa_admin_username, "password": qa_admin_password},
        {"username": qa_asociado_a_username, "password": qa_asociado_a_password},
        {"username": qa_asociado_b_username, "password": qa_asociado_b_password},
        {"username": qa_comercio_username, "password": qa_comercio_password},
    )
    qa_usernames = [credentials["username"] for credentials in qa_credentials]
    qa_passwords = [credentials["password"] for credentials in qa_credentials]

    if len(set(qa_usernames)) != len(qa_usernames):
        raise ValueError("Los usuarios QA deben ser distintos.")
    if len(set(qa_passwords)) != len(qa_passwords):
        raise ValueError("Las contraseñas QA deben ser distintas.")
    if user_model.objects.filter(username__in=qa_usernames).exists():
        raise ValueError("Un usuario QA coincide con un usuario copiado de Producción.")
    if Asociado.objects.filter(
        dni__in=[identity["dni"] for identity in QA_ASOCIADOS]
    ).exists():
        raise ValueError("Una identidad QA reservada ya existe en la copia.")
    for username, password in (
        (credentials["username"], credentials["password"])
        for credentials in qa_credentials
    ):
        if not username.startswith("qa-"):
            raise ValueError("Los usuarios exclusivos de staging deben comenzar con qa-.")
        if len(password) < 16:
            raise ValueError("Las contraseñas QA deben tener al menos 16 caracteres.")
        if password == username:
            raise ValueError("Una contraseña QA no puede coincidir con el usuario.")

    sesiones_eliminadas, _ = Session.objects.all().delete()
    usuarios_invalidados = user_model.objects.update(
        is_active=False,
        is_staff=False,
        is_superuser=False,
        password=make_password(None),
    )

    asociados = list(Asociado.objects.only("pk", "token_credencial"))
    old_tokens = {asociado.token_credencial for asociado in asociados}
    for asociado, token in zip(
        asociados,
        _new_credential_tokens(len(asociados), old_tokens),
        strict=True,
    ):
        asociado.token_credencial = token
    Asociado.objects.bulk_update(asociados, ["token_credencial"])

    ensure_default_groups()
    user_model.objects.create_superuser(
        username=qa_admin_username,
        email="",
        password=qa_admin_password,
    )
    asociado_group = Group.objects.get(name=ASOCIADO_GROUP)
    for credentials, identity in zip(
        qa_credentials[1:3],
        QA_ASOCIADOS,
        strict=True,
    ):
        _create_qa_asociado(
            user_model=user_model,
            group=asociado_group,
            credentials=credentials,
            identity=identity,
        )
    _create_qa_comercio(
        user_model=user_model,
        group=Group.objects.get(name=COMERCIO_GROUP),
        credentials=qa_credentials[3],
    )
    usuarios_qa_creados = len(qa_credentials)

    EstadoDatosStaging.objects.update_or_create(
        clave=EstadoDatosStaging.CLAVE_ACTUAL,
        defaults={
            "refresh_id": refresh_id,
            "listo_desde": timezone.now(),
        },
    )

    return StagingHardeningResult(
        sesiones_eliminadas=sesiones_eliminadas,
        usuarios_invalidados=usuarios_invalidados,
        tokens_regenerados=len(asociados),
        usuarios_qa_creados=usuarios_qa_creados,
    )
