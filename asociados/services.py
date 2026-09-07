from __future__ import annotations

import csv
import hashlib
import hmac
import secrets
import uuid
from dataclasses import dataclass
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from auditoria.models import EventoAuditoria
from auditoria.selectors import obtener_motivo_ultima_observacion_solicitud
from auditoria.services import construir_cambios, registrar_evento
from cuotas.services import generar_cuotas_iniciales_para_asociado
from usuarios.communications import programar_correo_alta_usuario
from usuarios.services import create_user_for_asociado, ensure_default_groups

from .communications import (
    programar_correo_datos_aprobados,
    programar_correo_correcciones_recibidas,
    programar_correo_solicitud_cancelada,
    programar_correo_solicitud_observada,
    programar_correo_solicitud_recibida,
)
from .models import (
    Asociado,
    ClasificacionAdherente,
    Curso,
    LimiteSolicitudPublica,
    SolicitudAsociacion,
)
from .validators import normalizar_documento


class SolicitudAsociacionDuplicada(Exception):
    pass


class LimiteSolicitudExcedido(Exception):
    pass


class EnlaceSolicitudInvalido(Exception):
    pass


class CorreccionSolicitudNoPermitida(Exception):
    pass


class TransicionSolicitudInvalida(Exception):
    pass


@dataclass(frozen=True)
class ResultadoTransicionSolicitud:
    solicitud: SolicitudAsociacion
    evento: EventoAuditoria
    token_seguimiento: str = ""


@dataclass(frozen=True)
class AltaDesdeSolicitudResult:
    solicitud: SolicitudAsociacion
    asociado: Asociado
    cuotas_generadas: tuple


@dataclass(frozen=True)
class AltaManualAsociadoResult:
    asociado: Asociado
    cuotas_generadas: tuple


CAMPOS_AUDITABLES_SOLICITUD = (
    "nombre",
    "apellido",
    "dni",
    "email",
    "telefono",
    "direccion",
    "es_estudiante_cet3",
    "tipo",
    "curso_actual",
    "clasificacion_adherente",
    "estado",
)


CAMPOS_AUDITABLES_ASOCIADO = (
    "nombre",
    "apellido",
    "dni",
    "email",
    "telefono",
    "direccion",
    "tipo",
    "curso_actual",
    "clasificacion_adherente",
    "estado",
    "fecha_alta",
    "fecha_inicio_cobro",
    "fecha_baja",
    "motivo_baja",
)

CAMPOS_DATOS_PROPIOS_ASOCIADO = (
    "nombre",
    "apellido",
    "telefono",
    "email",
    "direccion",
)


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def rotar_token_seguimiento(solicitud, ahora=None) -> str:
    ahora = ahora or timezone.now()
    token = secrets.token_urlsafe(32)
    solicitud.token_seguimiento_hash = _hash_token(token)
    solicitud.token_seguimiento_vence_en = ahora + timedelta(
        days=settings.UNI2_SOLICITUD_TOKEN_TTL_DAYS
    )
    if solicitud.pk:
        solicitud.save(
            update_fields=("token_seguimiento_hash", "token_seguimiento_vence_en")
        )
    return token


@transaction.atomic
def consumir_limite_publico(
    *,
    accion,
    clave_cruda,
    max_intentos,
    ventana,
    ahora=None,
):
    ahora = ahora or timezone.now()
    segundos_ventana = int(ventana.total_seconds())
    if segundos_ventana <= 0:
        raise ValueError("La ventana del límite debe ser positiva.")
    segundos_transcurridos = int(ahora.timestamp()) % segundos_ventana
    ventana_inicio = ahora - timedelta(
        seconds=segundos_transcurridos,
        microseconds=ahora.microsecond,
    )
    clave_hash = hmac.new(
        settings.SECRET_KEY.encode(),
        (clave_cruda or "sin-direccion").encode(),
        hashlib.sha256,
    ).hexdigest()
    LimiteSolicitudPublica.objects.filter(
        accion=accion,
        ventana_inicio__lt=ventana_inicio,
    ).delete()
    contador, _ = LimiteSolicitudPublica.objects.select_for_update().get_or_create(
        accion=accion,
        clave_hash=clave_hash,
        ventana_inicio=ventana_inicio,
    )
    if contador.intentos >= max_intentos:
        raise LimiteSolicitudExcedido()
    contador.intentos += 1
    contador.save(update_fields=("intentos",))
    return contador


def _existe_asociado_con_documento_normalizado(dni_normalizado: str) -> bool:
    for dni in Asociado.objects.values_list("dni", flat=True).iterator():
        try:
            if normalizar_documento(dni) == dni_normalizado:
                return True
        except ValidationError:
            continue
    return False


def crear_solicitud_asociacion(*, datos: dict, actor_ip: str, ahora=None):
    ahora = ahora or timezone.now()
    consumir_limite_publico(
        accion="crear_solicitud",
        clave_cruda=actor_ip,
        max_intentos=settings.UNI2_SOLICITUD_CREACION_MAX_INTENTOS,
        ventana=timedelta(minutes=settings.UNI2_SOLICITUD_CREACION_VENTANA_MINUTOS),
        ahora=ahora,
    )
    return _crear_solicitud_asociacion_transaccional(datos=datos, ahora=ahora)


@transaction.atomic
def _crear_solicitud_asociacion_transaccional(*, datos: dict, ahora):
    reintento = _obtener_reintento_preinscripcion(datos)
    if reintento is not None:
        return reintento

    dni_normalizado = normalizar_documento(datos.get("dni", ""))
    solicitud_abierta = SolicitudAsociacion.objects.filter(
        dni_normalizado=dni_normalizado
    ).exclude(estado=SolicitudAsociacion.ESTADO_CANCELADA)
    if solicitud_abierta.exists() or _existe_asociado_con_documento_normalizado(
        dni_normalizado
    ):
        reintento = _obtener_reintento_preinscripcion(datos)
        if reintento is not None:
            return reintento
        raise SolicitudAsociacionDuplicada()

    token = secrets.token_urlsafe(32)
    solicitud = SolicitudAsociacion(
        **datos,
        token_seguimiento_hash=_hash_token(token),
        token_seguimiento_vence_en=ahora
        + timedelta(days=settings.UNI2_SOLICITUD_TOKEN_TTL_DAYS),
    )
    try:
        solicitud.full_clean()
        with transaction.atomic():
            solicitud.save()
    except (IntegrityError, ValidationError) as error:
        reintento = _obtener_reintento_preinscripcion(datos)
        if reintento is not None:
            return reintento
        if isinstance(error, ValidationError) and not solicitud_abierta.exists():
            raise
        # Otra petición puede haber registrado el mismo documento entre la
        # consulta anterior y este INSERT. La restricción de la base es la
        # última defensa y se traduce al mismo resultado funcional.
        raise SolicitudAsociacionDuplicada() from error

    nuevos = {
        campo: getattr(solicitud, campo) for campo in CAMPOS_AUDITABLES_SOLICITUD
    }
    registrar_evento(
        actor=None,
        actor_etiqueta="Solicitante desde el sitio público",
        accion=EventoAuditoria.ACCION_CREAR,
        entidad=solicitud._meta.label,
        objeto_id=solicitud.pk,
        objeto_descripcion=str(solicitud),
        cambios=construir_cambios(
            anteriores={campo: None for campo in CAMPOS_AUDITABLES_SOLICITUD},
            nuevos=nuevos,
            campos=CAMPOS_AUDITABLES_SOLICITUD,
        ),
        origen=EventoAuditoria.ORIGEN_SITIO_PUBLICO,
    )
    programar_correo_solicitud_recibida(solicitud=solicitud, token=token)
    return solicitud


def _obtener_reintento_preinscripcion(datos):
    clave = datos.get("clave_operacion")
    if not clave:
        return None
    solicitud = SolicitudAsociacion.objects.filter(clave_operacion=clave).first()
    if solicitud is not None and (
        solicitud.dni_normalizado != normalizar_documento(datos.get("dni", ""))
        or solicitud.email.casefold() != datos.get("email", "").casefold()
    ):
        raise SolicitudAsociacionDuplicada()
    return solicitud


def _registrar_transicion_solicitud(
    *,
    solicitud,
    estado_anterior,
    actor,
    motivo="",
    operacion_id=None,
):
    return registrar_evento(
        actor=actor,
        accion=EventoAuditoria.ACCION_CAMBIAR_ESTADO,
        entidad=solicitud._meta.label,
        objeto_id=solicitud.pk,
        objeto_descripcion=str(solicitud),
        cambios={
            "estado": {
                "anterior": estado_anterior,
                "nuevo": solicitud.estado,
            }
        },
        motivo=motivo,
        origen=EventoAuditoria.ORIGEN_GESTION,
        operacion_id=operacion_id,
    )


@transaction.atomic
def observar_solicitud_asociacion(
    *,
    solicitud_id: int,
    explicacion: str,
    actor,
    ahora=None,
):
    explicacion = (explicacion or "").strip()
    if not explicacion:
        raise ValueError("La observación requiere una explicación.")
    ahora = ahora or timezone.now()
    solicitud = SolicitudAsociacion.objects.select_for_update().get(pk=solicitud_id)
    if solicitud.estado not in {
        SolicitudAsociacion.ESTADO_RECIBIDA,
        SolicitudAsociacion.ESTADO_DATOS_APROBADOS,
    }:
        raise TransicionSolicitudInvalida()

    estado_anterior = solicitud.estado
    token = secrets.token_urlsafe(32)
    solicitud.estado = SolicitudAsociacion.ESTADO_OBSERVADA
    solicitud.revisado_en = ahora
    solicitud.modificado_por = actor
    solicitud.token_seguimiento_hash = _hash_token(token)
    solicitud.token_seguimiento_vence_en = ahora + timedelta(
        days=settings.UNI2_SOLICITUD_TOKEN_TTL_DAYS
    )
    solicitud.save(
        update_fields=(
            "estado",
            "revisado_en",
            "modificado_en",
            "modificado_por",
            "token_seguimiento_hash",
            "token_seguimiento_vence_en",
        )
    )
    evento = _registrar_transicion_solicitud(
        solicitud=solicitud,
        estado_anterior=estado_anterior,
        actor=actor,
        motivo=explicacion,
    )
    programar_correo_solicitud_observada(
        solicitud=solicitud,
        token=token,
        explicacion=explicacion,
        operacion_id=evento.operacion_id,
        actor=actor,
    )
    return ResultadoTransicionSolicitud(
        solicitud=solicitud,
        evento=evento,
        token_seguimiento=token,
    )


@transaction.atomic
def aprobar_datos_solicitud_asociacion(*, solicitud_id: int, actor, ahora=None):
    ahora = ahora or timezone.now()
    solicitud = SolicitudAsociacion.objects.select_for_update().get(pk=solicitud_id)
    if solicitud.estado != SolicitudAsociacion.ESTADO_RECIBIDA:
        raise TransicionSolicitudInvalida()

    estado_anterior = solicitud.estado
    solicitud.estado = SolicitudAsociacion.ESTADO_DATOS_APROBADOS
    solicitud.revisado_en = ahora
    solicitud.modificado_por = actor
    solicitud.full_clean()
    solicitud.save(
        update_fields=("estado", "revisado_en", "modificado_en", "modificado_por")
    )
    evento = _registrar_transicion_solicitud(
        solicitud=solicitud,
        estado_anterior=estado_anterior,
        actor=actor,
    )
    programar_correo_datos_aprobados(
        solicitud=solicitud,
        operacion_id=evento.operacion_id,
        actor=actor,
    )
    return ResultadoTransicionSolicitud(solicitud=solicitud, evento=evento)


@transaction.atomic
def cancelar_solicitud_asociacion(
    *,
    solicitud_id: int,
    motivo: str,
    actor,
    ahora=None,
):
    motivo = (motivo or "").strip()
    if not motivo:
        raise ValueError("La cancelación requiere un motivo.")
    ahora = ahora or timezone.now()
    solicitud = SolicitudAsociacion.objects.select_for_update().get(pk=solicitud_id)
    if solicitud.estado not in {
        SolicitudAsociacion.ESTADO_RECIBIDA,
        SolicitudAsociacion.ESTADO_OBSERVADA,
        SolicitudAsociacion.ESTADO_DATOS_APROBADOS,
    }:
        raise TransicionSolicitudInvalida()

    estado_anterior = solicitud.estado
    solicitud.estado = SolicitudAsociacion.ESTADO_CANCELADA
    solicitud.finalizado_en = ahora
    solicitud.modificado_por = actor
    solicitud.save(
        update_fields=("estado", "finalizado_en", "modificado_en", "modificado_por")
    )
    evento = _registrar_transicion_solicitud(
        solicitud=solicitud,
        estado_anterior=estado_anterior,
        actor=actor,
        motivo=motivo,
    )
    programar_correo_solicitud_cancelada(
        solicitud=solicitud,
        motivo=motivo,
        operacion_id=evento.operacion_id,
        actor=actor,
    )
    return ResultadoTransicionSolicitud(solicitud=solicitud, evento=evento)


@transaction.atomic
def reenviar_comunicacion_solicitud(*, solicitud_id: int, actor, ahora=None):
    ahora = ahora or timezone.now()
    solicitud = SolicitudAsociacion.objects.select_for_update().get(pk=solicitud_id)
    operacion_id = uuid.uuid4()
    if solicitud.estado in {
        SolicitudAsociacion.ESTADO_RECIBIDA,
        SolicitudAsociacion.ESTADO_OBSERVADA,
    }:
        token = secrets.token_urlsafe(32)
        solicitud.token_seguimiento_hash = _hash_token(token)
        solicitud.token_seguimiento_vence_en = ahora + timedelta(
            days=settings.UNI2_SOLICITUD_TOKEN_TTL_DAYS
        )
        solicitud.modificado_por = actor
        solicitud.save(
            update_fields=(
                "token_seguimiento_hash",
                "token_seguimiento_vence_en",
                "modificado_en",
                "modificado_por",
            )
        )
        if solicitud.estado == SolicitudAsociacion.ESTADO_RECIBIDA:
            return programar_correo_solicitud_recibida(
                solicitud=solicitud,
                token=token,
                clave_sufijo=f"reenvio:{operacion_id}",
                actor=actor,
            )
        explicacion = obtener_motivo_ultima_observacion_solicitud(solicitud.pk)
        return programar_correo_solicitud_observada(
            solicitud=solicitud,
            token=token,
            explicacion=explicacion,
            operacion_id=f"reenvio:{operacion_id}",
            actor=actor,
        )
    if solicitud.estado == SolicitudAsociacion.ESTADO_DATOS_APROBADOS:
        return programar_correo_datos_aprobados(
            solicitud=solicitud,
            operacion_id=f"reenvio:{operacion_id}",
            actor=actor,
        )
    if solicitud.estado == SolicitudAsociacion.ESTADO_CANCELADA:
        motivo = (
            EventoAuditoria.objects.filter(
                entidad=solicitud._meta.label,
                objeto_id=str(solicitud.pk),
                cambios__estado__nuevo=SolicitudAsociacion.ESTADO_CANCELADA,
            )
            .exclude(motivo="")
            .order_by("-fecha", "-id")
            .values_list("motivo", flat=True)
            .first()
            or "La solicitud fue cerrada por la Mutual."
        )
        return programar_correo_solicitud_cancelada(
            solicitud=solicitud,
            motivo=motivo,
            operacion_id=f"reenvio:{operacion_id}",
            actor=actor,
        )
    raise TransicionSolicitudInvalida()


@transaction.atomic
def completar_alta_solicitud_asociacion(
    *,
    solicitud_id: int,
    actor,
    ahora=None,
):
    ahora = ahora or timezone.now()
    solicitud = SolicitudAsociacion.objects.select_for_update().get(pk=solicitud_id)
    if solicitud.estado != SolicitudAsociacion.ESTADO_DATOS_APROBADOS:
        raise TransicionSolicitudInvalida()
    solicitud.full_clean()
    if _existe_asociado_con_documento_normalizado(solicitud.dni_normalizado):
        raise SolicitudAsociacionDuplicada()

    operacion_id = uuid.uuid4()
    asociado = create_asociado(
        nombre=solicitud.nombre,
        apellido=solicitud.apellido,
        dni=solicitud.dni_normalizado,
        tipo=solicitud.tipo,
        fecha_alta=timezone.localdate(ahora),
        curso_actual=solicitud.curso_actual,
        clasificacion_adherente=solicitud.clasificacion_adherente,
        email=solicitud.email,
        telefono=solicitud.telefono,
        direccion=solicitud.direccion,
        actor=actor,
        operacion_id=operacion_id,
        enviar_correo_alta=True,
    )
    cuotas = generar_cuotas_iniciales_para_asociado(
        asociado=asociado,
        fecha_referencia=timezone.localdate(ahora),
        actor=actor,
        operacion_id=operacion_id,
    )
    estado_anterior = solicitud.estado
    solicitud.asociado = asociado
    solicitud.estado = SolicitudAsociacion.ESTADO_ALTA_COMPLETADA
    solicitud.finalizado_en = ahora
    solicitud.modificado_por = actor
    solicitud.save(
        update_fields=(
            "asociado",
            "estado",
            "finalizado_en",
            "modificado_en",
            "modificado_por",
        )
    )
    _registrar_transicion_solicitud(
        solicitud=solicitud,
        estado_anterior=estado_anterior,
        actor=actor,
        operacion_id=operacion_id,
    )
    return AltaDesdeSolicitudResult(
        solicitud=solicitud,
        asociado=asociado,
        cuotas_generadas=tuple(cuotas),
    )


def corregir_solicitud_asociacion(
    *,
    solicitud_id: int,
    datos: dict,
    token: str,
    actor_ip: str,
    ahora=None,
):
    ahora = ahora or timezone.now()
    solicitud = SolicitudAsociacion.objects.get(pk=solicitud_id)
    _validar_acceso_correccion(solicitud=solicitud, token=token, ahora=ahora)

    consumir_limite_publico(
        accion="corregir_solicitud",
        clave_cruda=str(solicitud.pk),
        max_intentos=settings.UNI2_SOLICITUD_CORRECCION_MAX_INTENTOS,
        ventana=timedelta(
            minutes=settings.UNI2_SOLICITUD_CORRECCION_VENTANA_MINUTOS
        ),
        ahora=ahora,
    )
    return _corregir_solicitud_asociacion_transaccional(
        solicitud_id=solicitud_id,
        datos=datos,
        token=token,
        ahora=ahora,
    )


def _validar_acceso_correccion(*, solicitud, token, ahora):
    if not hmac.compare_digest(solicitud.token_seguimiento_hash, _hash_token(token)):
        raise EnlaceSolicitudInvalido()
    if solicitud.token_seguimiento_vence_en <= ahora:
        raise EnlaceSolicitudInvalido()
    if solicitud.estado != SolicitudAsociacion.ESTADO_OBSERVADA:
        raise CorreccionSolicitudNoPermitida()


@transaction.atomic
def _corregir_solicitud_asociacion_transaccional(
    *,
    solicitud_id: int,
    datos: dict,
    token: str,
    ahora,
):
    solicitud = SolicitudAsociacion.objects.select_for_update().get(pk=solicitud_id)
    # Se vuelve a validar después del bloqueo porque otra petición pudo usar el
    # enlace mientras se consumía el límite fuera de esta transacción.
    _validar_acceso_correccion(solicitud=solicitud, token=token, ahora=ahora)

    dni_normalizado = normalizar_documento(datos.get("dni", ""))
    otra_solicitud = (
        SolicitudAsociacion.objects.filter(dni_normalizado=dni_normalizado)
        .exclude(pk=solicitud.pk)
        .exclude(estado=SolicitudAsociacion.ESTADO_CANCELADA)
    )
    if otra_solicitud.exists() or _existe_asociado_con_documento_normalizado(
        dni_normalizado
    ):
        raise SolicitudAsociacionDuplicada()

    anteriores = {
        campo: getattr(solicitud, campo) for campo in CAMPOS_AUDITABLES_SOLICITUD
    }
    for campo in (
        "nombre",
        "apellido",
        "dni",
        "email",
        "telefono",
        "direccion",
        "es_estudiante_cet3",
        "curso_actual",
        "clasificacion_adherente",
    ):
        setattr(solicitud, campo, datos[campo])
    solicitud.estado = SolicitudAsociacion.ESTADO_RECIBIDA
    solicitud.modificado_por = None
    nuevo_token = secrets.token_urlsafe(32)
    solicitud.token_seguimiento_hash = _hash_token(nuevo_token)
    solicitud.token_seguimiento_vence_en = ahora + timedelta(
        days=settings.UNI2_SOLICITUD_TOKEN_TTL_DAYS
    )
    solicitud.full_clean()
    try:
        with transaction.atomic():
            solicitud.save()
    except IntegrityError as error:
        raise SolicitudAsociacionDuplicada() from error

    nuevos = {
        campo: getattr(solicitud, campo) for campo in CAMPOS_AUDITABLES_SOLICITUD
    }
    evento = registrar_evento(
        actor=None,
        actor_etiqueta="Solicitante mediante enlace privado",
        accion=EventoAuditoria.ACCION_MODIFICAR,
        entidad=solicitud._meta.label,
        objeto_id=solicitud.pk,
        objeto_descripcion=str(solicitud),
        cambios=construir_cambios(
            anteriores=anteriores,
            nuevos=nuevos,
            campos=CAMPOS_AUDITABLES_SOLICITUD,
        ),
        origen=EventoAuditoria.ORIGEN_SITIO_PUBLICO,
    )
    programar_correo_correcciones_recibidas(
        solicitud=solicitud,
        token=nuevo_token,
        operacion_id=evento.operacion_id,
    )
    return solicitud


def _valores_auditables_asociado(asociado):
    return {campo: getattr(asociado, campo) for campo in CAMPOS_AUDITABLES_ASOCIADO}


def calculate_fecha_inicio_cobro(fecha_alta: date, tipo: str) -> date:
    inicio_mes = fecha_alta.replace(day=1)
    if tipo == Asociado.TIPO_ADHERENTE:
        return inicio_mes
    if tipo != Asociado.TIPO_ASOCIADO:
        raise ValueError("Tipo de asociado inválido.")

    indice_mes = inicio_mes.year * 12 + inicio_mes.month - 1 - 2
    anio, mes_desde_cero = divmod(indice_mes, 12)
    return date(anio, mes_desde_cero + 1, 1)


@transaction.atomic
def create_asociado(
    *,
    nombre: str,
    apellido: str,
    dni: str,
    tipo: str,
    fecha_alta: date | str,
    curso_actual: Curso | None = None,
    clasificacion_adherente=None,
    fecha_inicio_cobro: date | str | None = None,
    email: str = "",
    telefono: str = "",
    direccion: str = "",
    actor=None,
    origen: str = EventoAuditoria.ORIGEN_GESTION,
    operacion_id=None,
    enviar_correo_alta: bool = False,
):
    operacion_id = operacion_id or uuid.uuid4()
    if isinstance(fecha_alta, str):
        fecha_alta = date.fromisoformat(fecha_alta)
    if isinstance(fecha_inicio_cobro, str):
        fecha_inicio_cobro = date.fromisoformat(fecha_inicio_cobro)

    if Asociado.objects.filter(dni=dni).exists():
        raise ValueError("Ya existe un asociado con ese DNI.")

    fecha_inicio = fecha_inicio_cobro or calculate_fecha_inicio_cobro(fecha_alta, tipo)
    if tipo == Asociado.TIPO_ASOCIADO:
        clasificacion_adherente = None
    else:
        curso_actual = None
        if clasificacion_adherente is None:
            clasificacion_adherente = ClasificacionAdherente.objects.get(
                nombre=ClasificacionAdherente.NOMBRE_SIN_CLASIFICAR
            )
    asociado = Asociado.objects.create(
        nombre=nombre,
        apellido=apellido,
        dni=dni,
        tipo=tipo,
        curso_actual=curso_actual,
        clasificacion_adherente=clasificacion_adherente,
        fecha_alta=fecha_alta,
        fecha_inicio_cobro=fecha_inicio,
        email=email,
        telefono=telefono,
        direccion=direccion,
    )

    ensure_default_groups()
    usuario = create_user_for_asociado(
        asociado=asociado,
        password=dni,
        actor=actor,
        operacion_id=operacion_id,
    )
    if enviar_correo_alta:
        programar_correo_alta_usuario(
            asociado=asociado,
            usuario=usuario,
            actor=actor,
        )

    if actor is not None:
        nuevos = _valores_auditables_asociado(asociado)
        registrar_evento(
            actor=actor,
            accion=EventoAuditoria.ACCION_CREAR,
            entidad="asociados.Asociado",
            objeto_id=asociado.pk,
            objeto_descripcion=str(asociado),
            cambios=construir_cambios(
                anteriores={campo: None for campo in CAMPOS_AUDITABLES_ASOCIADO},
                nuevos=nuevos,
                campos=CAMPOS_AUDITABLES_ASOCIADO,
            ),
            origen=origen,
            operacion_id=operacion_id,
        )

    return asociado


@transaction.atomic
def crear_asociado_con_cuotas_iniciales(
    *,
    nombre: str,
    apellido: str,
    dni: str,
    tipo: str,
    fecha_alta: date | str,
    curso_actual: Curso | None = None,
    clasificacion_adherente=None,
    email: str = "",
    telefono: str = "",
    direccion: str = "",
    actor=None,
) -> AltaManualAsociadoResult:
    """Completa el alta manual y sus cuotas como una única operación."""

    operacion_id = uuid.uuid4()
    asociado = create_asociado(
        nombre=nombre,
        apellido=apellido,
        dni=dni,
        tipo=tipo,
        fecha_alta=fecha_alta,
        curso_actual=curso_actual,
        clasificacion_adherente=clasificacion_adherente,
        email=email,
        telefono=telefono,
        direccion=direccion,
        actor=actor,
        operacion_id=operacion_id,
        enviar_correo_alta=True,
    )
    cuotas = generar_cuotas_iniciales_para_asociado(
        asociado=asociado,
        fecha_referencia=asociado.fecha_alta,
        actor=actor,
        operacion_id=operacion_id,
    )
    return AltaManualAsociadoResult(
        asociado=asociado,
        cuotas_generadas=tuple(cuotas),
    )


@transaction.atomic
def actualizar_asociado(
    *,
    asociado: Asociado,
    datos,
    campos_modificados,
    actor,
    origen=EventoAuditoria.ORIGEN_GESTION,
):
    campos = [campo for campo in campos_modificados if campo in CAMPOS_AUDITABLES_ASOCIADO]
    if not campos:
        return asociado

    asociado_anterior = Asociado.objects.select_related("curso_actual").get(pk=asociado.pk)
    anteriores = _valores_auditables_asociado(asociado_anterior)
    for campo in campos:
        setattr(asociado, campo, datos[campo])
    asociado.save(update_fields=campos)
    nuevos = _valores_auditables_asociado(asociado)
    cambios = construir_cambios(anteriores=anteriores, nuevos=nuevos, campos=campos)
    if cambios:
        registrar_evento(
            actor=actor,
            accion=EventoAuditoria.ACCION_MODIFICAR,
            entidad="asociados.Asociado",
            objeto_id=asociado.pk,
            objeto_descripcion=str(asociado),
            cambios=cambios,
            origen=origen,
        )
    return asociado


@transaction.atomic
def actualizar_datos_propios_asociado(
    *, asociado: Asociado, datos, actor
) -> Asociado:
    asociado = Asociado.objects.select_for_update().get(pk=asociado.pk)
    if asociado.usuario_id != actor.pk:
        raise PermissionDenied(
            "No podés modificar los datos de otro asociado."
        )
    usuario = get_user_model().objects.select_for_update().get(
        pk=asociado.usuario_id
    )

    campos_modificados = [
        campo
        for campo in CAMPOS_DATOS_PROPIOS_ASOCIADO
        if getattr(asociado, campo) != datos[campo]
    ]
    asociado = actualizar_asociado(
        asociado=asociado,
        datos=datos,
        campos_modificados=campos_modificados,
        actor=actor,
        origen=EventoAuditoria.ORIGEN_ASOCIADO,
    )

    valores_usuario = {
        "first_name": asociado.nombre,
        "last_name": asociado.apellido,
        "email": asociado.email,
    }
    campos_usuario = [
        campo
        for campo, valor in valores_usuario.items()
        if getattr(usuario, campo) != valor
    ]
    for campo in campos_usuario:
        setattr(usuario, campo, valores_usuario[campo])
    if campos_usuario:
        usuario.save(update_fields=campos_usuario)
    return asociado


@transaction.atomic
def dar_baja_asociado(
    asociado: Asociado,
    fecha_baja: date,
    motivo_baja: str,
    *,
    actor=None,
):
    anteriores = {
        "estado": asociado.estado,
        "fecha_baja": asociado.fecha_baja,
        "motivo_baja": asociado.motivo_baja,
    }
    asociado.estado = Asociado.ESTADO_INACTIVO
    asociado.fecha_baja = fecha_baja
    asociado.motivo_baja = motivo_baja
    asociado.save(update_fields=["estado", "fecha_baja", "motivo_baja"])
    registrar_evento(
        actor=actor,
        actor_etiqueta="Sistema: baja de asociado",
        accion=EventoAuditoria.ACCION_CAMBIAR_ESTADO,
        entidad=asociado._meta.label,
        objeto_id=asociado.pk,
        objeto_descripcion=str(asociado),
        cambios=construir_cambios(
            anteriores=anteriores,
            nuevos={
                "estado": asociado.estado,
                "fecha_baja": asociado.fecha_baja,
                "motivo_baja": asociado.motivo_baja,
            },
            campos=("estado", "fecha_baja", "motivo_baja"),
        ),
        motivo=motivo_baja,
        origen=EventoAuditoria.ORIGEN_GESTION if actor else EventoAuditoria.ORIGEN_SISTEMA,
    )
    return asociado


@dataclass
class ImportResult:
    created: int = 0
    errors: list[str] | None = None

    def __post_init__(self):
        self.errors = self.errors or []


def import_asociados_from_csv(csv_file) -> ImportResult:
    result = ImportResult()
    reader = csv.DictReader(csv_file)
    for index, row in enumerate(reader, start=2):
        try:
            curso = None
            curso_str = (row.get("curso") or "").strip()
            if curso_str:
                partes = curso_str.split()
                filtro = {}
                if len(partes) >= 1:
                    filtro["anio"] = partes[0]
                if len(partes) >= 2:
                    filtro["curso"] = partes[1]
                if len(partes) >= 3:
                    filtro["division"] = partes[2]
                if len(partes) >= 4:
                    filtro["turno"] = partes[3]
                curso = Curso.objects.filter(**filtro).first()
                if curso is None:
                    raise ValueError(f"Curso inexistente: {curso_str}")

            create_asociado(
                nombre=row["nombre"].strip(),
                apellido=row["apellido"].strip(),
                dni=row["dni"].strip(),
                tipo=row["tipo"].strip(),
                fecha_alta=row["fecha_alta"].strip(),
                curso_actual=curso,
                email=(row.get("email") or "").strip(),
                telefono=(row.get("telefono") or "").strip(),
            )
            result.created += 1
        except Exception as exc:  # noqa: BLE001
            result.errors.append(f"Fila {index}: {exc}")
    return result
