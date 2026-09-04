from django.conf import settings
from django.urls import reverse

from comunicaciones.services import programar_email_transaccional


def _url_absoluta(view_name: str) -> str:
    return f"{settings.UNI2_SITE_URL.rstrip('/')}{reverse(view_name)}"


def programar_correo_alta_usuario(*, asociado, usuario, actor=None):
    if not asociado.email:
        return None

    return programar_email_transaccional(
        tipo="alta_usuario",
        destino=asociado.email,
        clave_idempotencia=f"asociado:{asociado.pk}:alta-usuario",
        origen_entidad=asociado._meta.label,
        origen_id=asociado.pk,
        contexto={
            "nombre": asociado.nombre,
            "username": usuario.get_username(),
            "password_inicial": asociado.dni,
            "login_url": _url_absoluta("usuarios:login"),
        },
        actor=actor,
    )


def programar_correo_recuperacion_contrasena(
    *, asociado, usuario, recuperacion_url: str, operacion_id
):
    return programar_email_transaccional(
        tipo="recuperacion_contrasena",
        destino=asociado.email,
        clave_idempotencia=(
            f"usuario:{usuario.pk}:recuperacion:{operacion_id}"
        ),
        origen_entidad=usuario._meta.label,
        origen_id=usuario.pk,
        contexto={
            "nombre": asociado.nombre,
            "recuperacion_url": recuperacion_url,
        },
    )
