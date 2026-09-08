from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.db import transaction
from django.utils import timezone

from asociados.models import Asociado
from comercios.models import Comercio

from .models import EstadoDatosStaging


@dataclass(frozen=True)
class StagingHardeningResult:
    sesiones_eliminadas: int
    usuarios_conservados: int


@dataclass(frozen=True)
class StagingPasswordRotationResult:
    usuarios_actualizados: int


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
MIN_QA_PASSWORD_LENGTH = 8


@transaction.atomic
def harden_staging_clone(*, refresh_id):
    """Elimina sesiones copiadas y conserva intactas las cuentas productivas."""

    user_model = get_user_model()

    sesiones_eliminadas, _ = Session.objects.all().delete()
    usuarios_conservados = user_model.objects.count()

    EstadoDatosStaging.objects.update_or_create(
        clave=EstadoDatosStaging.CLAVE_ACTUAL,
        defaults={
            "refresh_id": refresh_id,
            "listo_desde": timezone.now(),
        },
    )

    return StagingHardeningResult(
        sesiones_eliminadas=sesiones_eliminadas,
        usuarios_conservados=usuarios_conservados,
    )


@transaction.atomic
def rotate_staging_qa_passwords(*, credentials):
    """Actualiza sólo las contraseñas de las cuatro cuentas QA de staging."""

    user_model = get_user_model()
    expected_roles = (
        ("admin", credentials["admin"], lambda user: user.is_staff and user.is_superuser),
        (
            "asociado_a",
            credentials["asociado_a"],
            lambda user: user.asociado.dni == QA_ASOCIADOS[0]["dni"],
        ),
        (
            "asociado_b",
            credentials["asociado_b"],
            lambda user: user.asociado.dni == QA_ASOCIADOS[1]["dni"],
        ),
        (
            "comercio",
            credentials["comercio"],
            lambda user: user.comercio.nombre == QA_COMERCIO_NAME,
        ),
    )
    usernames = [item[1]["username"] for item in expected_roles]
    passwords = [item[1]["password"] for item in expected_roles]

    if len(set(usernames)) != len(usernames):
        raise ValueError("Los usuarios QA deben ser distintos.")
    if len(set(passwords)) != len(passwords):
        raise ValueError("Las contraseñas QA deben ser distintas.")
    for username, password in zip(usernames, passwords, strict=True):
        if not username.startswith("qa-"):
            raise ValueError("Los usuarios exclusivos de staging deben comenzar con qa-.")
        if len(password) < MIN_QA_PASSWORD_LENGTH:
            raise ValueError(
                f"Las contraseñas QA deben tener al menos {MIN_QA_PASSWORD_LENGTH} caracteres."
            )
        if password == username:
            raise ValueError("Una contraseña QA no puede coincidir con el usuario.")

    users = {user.username: user for user in user_model.objects.filter(username__in=usernames)}
    if len(users) != len(usernames):
        raise ValueError("Deben existir las cuatro cuentas QA antes de rotar sus contraseñas.")

    for role, credentials_for_user, matches_role in expected_roles:
        user = users[credentials_for_user["username"]]
        try:
            role_matches = matches_role(user)
        except (AttributeError, Asociado.DoesNotExist, Comercio.DoesNotExist):
            role_matches = False
        if not role_matches:
            raise ValueError(f"La cuenta QA de {role} no coincide con su perfil esperado.")

    for credentials_for_user in (item[1] for item in expected_roles):
        user = users[credentials_for_user["username"]]
        user.set_password(credentials_for_user["password"])
        user.save(update_fields=["password"])

    return StagingPasswordRotationResult(usuarios_actualizados=len(users))
