import uuid
from dataclasses import dataclass, field
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from asociados.models import Asociado
from asociados.validators import normalizar_documento
from auditoria.models import EventoAuditoria
from auditoria.services import construir_cambios, registrar_evento
from comunicaciones.models import Comunicacion
from comercios.models import Comercio
from gestion.permissions import user_has_any_gestion_permission
from usuarios.communications import programar_correo_recuperacion_contrasena
from usuarios.roles import (
    ADMINISTRADOR_APP_GROUP,
    ASOCIADO_GROUP,
    ATENCION_ASOCIADO_GROUP,
    COMERCIO_GROUP,
    DEFAULT_GROUPS,
    ACCESO_ADMIN_TECNICO,
)


# Alias de transición para los llamadores existentes.
ADMIN_GROUP = ADMINISTRADOR_APP_GROUP
ATENCION_MUTUAL_GROUP = ATENCION_ASOCIADO_GROUP
AUDIT_FIELDS_USER = ("username", "email", "first_name", "last_name", "is_active", "is_staff", "groups")


def _snapshot_user(user):
    return {
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active,
        "is_staff": user.is_staff,
        "groups": list(user.groups.order_by("pk")),
    }


def _registrar_usuario_creado(*, user, actor, operacion_id):
    nuevos = _snapshot_user(user)
    registrar_evento(
        actor=actor,
        actor_etiqueta="Sistema: creación de usuario",
        accion=EventoAuditoria.ACCION_CREAR,
        entidad=user._meta.label,
        objeto_id=user.pk,
        objeto_descripcion=user.get_username(),
        cambios=construir_cambios(
            anteriores={field: None for field in AUDIT_FIELDS_USER},
            nuevos=nuevos,
            campos=AUDIT_FIELDS_USER,
        ),
        origen=EventoAuditoria.ORIGEN_GESTION if actor else EventoAuditoria.ORIGEN_SISTEMA,
        operacion_id=operacion_id,
    )


def _registrar_vinculacion(*, objeto, user, actor, operacion_id):
    registrar_evento(
        actor=actor,
        actor_etiqueta="Sistema: vinculación de usuario",
        accion=EventoAuditoria.ACCION_VINCULAR,
        entidad=objeto._meta.label,
        objeto_id=objeto.pk,
        objeto_descripcion=str(objeto),
        cambios={
            "usuario": {
                "anterior": None,
                "nuevo": {"id": user.pk, "texto": user.get_username()},
            }
        },
        origen=EventoAuditoria.ORIGEN_GESTION if actor else EventoAuditoria.ORIGEN_SISTEMA,
        operacion_id=operacion_id,
    )


@transaction.atomic
def _vincular_usuario_existente(*, asociado, user, group, actor):
    asociado.usuario = user
    asociado.save(update_fields=["usuario"])
    user.groups.add(group)
    if actor is not None:
        _registrar_vinculacion(
            objeto=asociado,
            user=user,
            actor=actor,
            operacion_id=uuid.uuid4(),
        )


@dataclass
class MissingAsociadoUsersResult:
    creados: int = 0
    vinculados: int = 0
    omitidos: int = 0
    procesados: int = 0
    restantes: int = 0
    siguiente_cursor: int | None = None
    hay_mas: bool = False
    errores: list[str] = field(default_factory=list)


def ensure_default_groups():
    for group_name in DEFAULT_GROUPS:
        Group.objects.get_or_create(name=group_name)


def sincronizar_acceso_admin(user):
    """Alinea ``is_staff`` con la capacidad explícita de acceso al admin."""

    # La instancia puede conservar caches de permisos anteriores al guardado de
    # la relación M2M. Se invalidan para evaluar la asignación recién persistida.
    for cache_name in ("_perm_cache", "_group_perm_cache", "_user_perm_cache"):
        if hasattr(user, cache_name):
            delattr(user, cache_name)
    requiere_admin = user.is_superuser or user.has_perm(ACCESO_ADMIN_TECNICO)
    if user.is_staff != requiere_admin:
        user.is_staff = requiere_admin
        user.save(update_fields=["is_staff"])
    return user


def user_has_group(user, group_name: str) -> bool:
    return user.is_authenticated and user.groups.filter(name=group_name).exists()


def user_is_asociado(user) -> bool:
    return user_has_group(user, ASOCIADO_GROUP) or hasattr(user, "asociado")


def user_is_comercio(user) -> bool:
    return user_has_group(user, COMERCIO_GROUP) or hasattr(user, "comercio")


def user_has_gestion_access(user) -> bool:
    return bool(
        user.is_authenticated
        and (
            user_has_any_gestion_permission(user)
            or user.has_perm(ACCESO_ADMIN_TECNICO)
        )
    )


def get_available_experiences(user) -> list[str]:
    if not user.is_authenticated:
        return []

    experiences = []
    if hasattr(user, "asociado"):
        experiences.append("asociado")
    if hasattr(user, "comercio"):
        experiences.append("comercio")
    if user_has_gestion_access(user):
        experiences.append("gestion")
    return experiences


def _buscar_asociado_recuperable(*, dni: str, email: str):
    try:
        dni_normalizado = normalizar_documento(dni)
    except ValidationError:
        return None

    email_normalizado = (email or "").strip()
    if not email_normalizado:
        return None

    candidatos = Asociado.objects.select_for_update().filter(
        email__iexact=email_normalizado,
        estado=Asociado.ESTADO_ACTIVO,
        usuario__isnull=False,
    )
    coincidencias = []
    for asociado in candidatos:
        try:
            dni_asociado = normalizar_documento(asociado.dni)
        except ValidationError:
            continue
        if dni_asociado == dni_normalizado:
            coincidencias.append(asociado)

    if len(coincidencias) != 1:
        return None
    return coincidencias[0], dni_normalizado, email_normalizado


def _datos_recuperacion_siguen_vigentes(
    *, asociado, usuario, dni_normalizado: str, email_normalizado: str
) -> bool:
    try:
        dni_actual = normalizar_documento(asociado.dni)
    except ValidationError:
        return False

    return bool(
        asociado.estado == Asociado.ESTADO_ACTIVO
        and asociado.usuario_id == usuario.pk
        and usuario.is_active
        and dni_actual == dni_normalizado
        and asociado.email.casefold() == email_normalizado.casefold()
    )


@transaction.atomic
def solicitar_recuperacion_contrasena(
    *, dni: str, email: str, ahora=None
) -> bool:
    ahora = ahora or timezone.now()
    coincidencia = _buscar_asociado_recuperable(dni=dni, email=email)
    if coincidencia is None:
        return False
    asociado, dni_normalizado, email_normalizado = coincidencia

    usuario = get_user_model().objects.select_for_update().get(
        pk=asociado.usuario_id
    )
    asociado.refresh_from_db(fields=("dni", "email", "estado", "usuario"))
    if not _datos_recuperacion_siguen_vigentes(
        asociado=asociado,
        usuario=usuario,
        dni_normalizado=dni_normalizado,
        email_normalizado=email_normalizado,
    ):
        return False
    desde = ahora - timedelta(
        minutes=settings.UNI2_PASSWORD_RESET_EMAIL_COOLDOWN_MINUTES
    )
    if Comunicacion.objects.filter(
        tipo="recuperacion_contrasena",
        origen_entidad=usuario._meta.label,
        origen_id=str(usuario.pk),
        creado_en__gte=desde,
    ).exists():
        return True

    uidb64 = urlsafe_base64_encode(force_bytes(usuario.pk))
    token = default_token_generator.make_token(usuario)
    recuperacion_path = reverse(
        "usuarios:restablecer_contrasena",
        kwargs={"uidb64": uidb64, "token": token},
    )
    recuperacion_url = (
        f"{settings.UNI2_SITE_URL.rstrip('/')}{recuperacion_path}"
    )
    programar_correo_recuperacion_contrasena(
        asociado=asociado,
        usuario=usuario,
        recuperacion_url=recuperacion_url,
        operacion_id=uuid.uuid4(),
    )
    return True


@transaction.atomic
def create_user_for_asociado(
    asociado: Asociado,
    password: str,
    email: str | None = None,
    *,
    actor=None,
    operacion_id=None,
):
    if asociado.usuario_id:
        raise ValueError("El asociado ya tiene un usuario vinculado.")

    user_model = get_user_model()
    username = str(asociado.dni)
    if user_model.objects.filter(username=username).exists():
        raise ValueError("Ya existe un usuario con ese username.")

    user = user_model.objects.create_user(
        username=username,
        email=email or asociado.email,
        password=password,
        first_name=asociado.nombre,
        last_name=asociado.apellido,
        is_active=True,
    )
    asociado.usuario = user
    asociado.save(update_fields=["usuario"])
    group = Group.objects.get(name=ASOCIADO_GROUP)
    user.groups.add(group)
    if actor is not None:
        operacion_id = operacion_id or uuid.uuid4()
        _registrar_usuario_creado(user=user, actor=actor, operacion_id=operacion_id)
        _registrar_vinculacion(objeto=asociado, user=user, actor=actor, operacion_id=operacion_id)
    return user


def create_missing_users_for_asociados(
    batch_size: int | None = None,
    after_id: int = 0,
    *,
    actor=None,
) -> MissingAsociadoUsersResult:
    result = MissingAsociadoUsersResult()
    result.omitidos = Asociado.objects.filter(usuario__isnull=False).count()
    asociados_qs = Asociado.objects.filter(usuario__isnull=True, id__gt=after_id).order_by("id")
    total_pendientes = asociados_qs.count()
    asociados = list(asociados_qs if batch_size is None else asociados_qs[:batch_size])
    result.procesados = len(asociados)
    result.restantes = max(total_pendientes - result.procesados, 0)
    result.hay_mas = result.restantes > 0
    if not asociados:
        return result

    user_model = get_user_model()
    asociado_group = Group.objects.get(name=ASOCIADO_GROUP)
    usuarios_existentes = user_model.objects.filter(username__in=[str(asociado.dni) for asociado in asociados])
    usuarios_existentes = {user.username: user for user in usuarios_existentes}

    for asociado in asociados:
        username = str(asociado.dni)
        existing_user = usuarios_existentes.get(username)
        if existing_user is not None:
            if hasattr(existing_user, "asociado"):
                result.errores.append(f"Asociado {asociado.dni}: el usuario existente ya está vinculado a otro asociado.")
                continue
            _vincular_usuario_existente(
                asociado=asociado,
                user=existing_user,
                group=asociado_group,
                actor=actor,
            )
            result.vinculados += 1
            continue

        try:
            crear_kwargs = {"asociado": asociado, "password": username}
            if actor is not None:
                crear_kwargs["actor"] = actor
            user = create_user_for_asociado(**crear_kwargs)
        except ValueError as exc:
            result.errores.append(f"Asociado {asociado.dni}: {exc}")
        except IntegrityError:
            existing_user = user_model.objects.filter(username=username).first()
            if existing_user is None:
                result.errores.append(f"Asociado {asociado.dni}: no se pudo crear el usuario.")
                continue
            if hasattr(existing_user, "asociado"):
                result.errores.append(f"Asociado {asociado.dni}: el usuario existente ya está vinculado a otro asociado.")
                continue
            _vincular_usuario_existente(
                asociado=asociado,
                user=existing_user,
                group=asociado_group,
                actor=actor,
            )
            usuarios_existentes[username] = existing_user
            result.vinculados += 1
        else:
            usuarios_existentes[username] = user
            result.creados += 1

    if asociados and result.hay_mas:
        result.siguiente_cursor = asociados[-1].id
    return result


@transaction.atomic
def create_user_for_comercio(
    comercio: Comercio,
    password: str,
    email: str | None = None,
    *,
    actor=None,
):
    if comercio.usuario_id:
        raise ValueError("El comercio ya tiene un usuario vinculado.")

    user_model = get_user_model()
    username = f"com-{comercio.id}"
    if user_model.objects.filter(username=username).exists():
        raise ValueError("Ya existe un usuario con ese username.")

    user = user_model.objects.create_user(
        username=username,
        email=email or comercio.email or "",
        password=password,
        first_name=comercio.nombre,
        last_name="",
        is_active=True,
    )
    comercio.usuario = user
    comercio.save(update_fields=["usuario"])
    group = Group.objects.get(name=COMERCIO_GROUP)
    user.groups.add(group)
    if actor is not None:
        operacion_id = uuid.uuid4()
        _registrar_usuario_creado(user=user, actor=actor, operacion_id=operacion_id)
        _registrar_vinculacion(objeto=comercio, user=user, actor=actor, operacion_id=operacion_id)
    return user
