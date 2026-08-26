from django.conf import settings

from comunicaciones.services import programar_email_transaccional


def construir_url_seguimiento(token: str) -> str:
    return f"{settings.UNI2_SITE_URL.rstrip('/')}/sumate/solicitud/{token}/"


def programar_correo_solicitud_recibida(
    *,
    solicitud,
    token: str,
    clave_sufijo="inicial",
    actor=None,
):
    return programar_email_transaccional(
        tipo="preinscripcion_recibida",
        destino=solicitud.email,
        clave_idempotencia=f"solicitud:{solicitud.pk}:recibida:{clave_sufijo}",
        origen_entidad=solicitud._meta.label,
        origen_id=solicitud.pk,
        contexto={
            "nombre": solicitud.nombre,
            "seguimiento_url": construir_url_seguimiento(token),
        },
        actor=actor or solicitud.creado_por,
    )


def programar_correo_correcciones_recibidas(*, solicitud, token: str, operacion_id):
    return programar_email_transaccional(
        tipo="preinscripcion_correcciones_recibidas",
        destino=solicitud.email,
        clave_idempotencia=f"solicitud:{solicitud.pk}:correcciones:{operacion_id}",
        origen_entidad=solicitud._meta.label,
        origen_id=solicitud.pk,
        contexto={
            "nombre": solicitud.nombre,
            "seguimiento_url": construir_url_seguimiento(token),
        },
    )


def programar_correo_solicitud_observada(
    *,
    solicitud,
    token,
    explicacion,
    operacion_id,
    actor,
):
    return programar_email_transaccional(
        tipo="preinscripcion_observada",
        destino=solicitud.email,
        clave_idempotencia=f"solicitud:{solicitud.pk}:observada:{operacion_id}",
        origen_entidad=solicitud._meta.label,
        origen_id=solicitud.pk,
        contexto={
            "nombre": solicitud.nombre,
            "explicacion": explicacion,
            "seguimiento_url": construir_url_seguimiento(token),
        },
        actor=actor,
    )


def programar_correo_datos_aprobados(*, solicitud, operacion_id, actor):
    return programar_email_transaccional(
        tipo="preinscripcion_datos_aprobados",
        destino=solicitud.email,
        clave_idempotencia=f"solicitud:{solicitud.pk}:datos-aprobados:{operacion_id}",
        origen_entidad=solicitud._meta.label,
        origen_id=solicitud.pk,
        contexto={"nombre": solicitud.nombre},
        actor=actor,
    )


def programar_correo_solicitud_cancelada(
    *,
    solicitud,
    motivo,
    operacion_id,
    actor,
):
    return programar_email_transaccional(
        tipo="preinscripcion_cancelada",
        destino=solicitud.email,
        clave_idempotencia=f"solicitud:{solicitud.pk}:cancelada:{operacion_id}",
        origen_entidad=solicitud._meta.label,
        origen_id=solicitud.pk,
        contexto={"nombre": solicitud.nombre, "motivo": motivo},
        actor=actor,
    )
