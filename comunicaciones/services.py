from dataclasses import dataclass

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone

from .email_types import EMAIL_TYPES
from .models import Comunicacion, EntregaComunicacion


@dataclass(frozen=True)
class RenderedEmail:
    subject: str
    text: str
    html: str


def render_email(*, tipo: str, contexto: dict) -> RenderedEmail:
    email_type = EMAIL_TYPES[tipo]
    return RenderedEmail(
        subject=email_type.subject,
        text=render_to_string(f"{email_type.template_base}.txt", contexto).strip(),
        html=render_to_string(f"{email_type.template_base}.html", contexto).strip(),
    )


def resolver_entrega_email(*, destino: str, subject: str) -> tuple[list[str], str]:
    if settings.UNI2_TRANSACTIONAL_EMAIL_MODE != "redirect":
        return [destino], subject

    redirect_to = settings.UNI2_TRANSACTIONAL_EMAIL_REDIRECT_TO.strip()
    if not redirect_to:
        raise ImproperlyConfigured(
            "El modo redirect requiere un destinatario seguro."
        )
    return [redirect_to], f"[STAGING] {subject}"


def resumir_error_entrega(error: Exception) -> str:
    mensaje = str(error)
    email_password = getattr(settings, "EMAIL_HOST_PASSWORD", "")
    if email_password:
        mensaje = mensaje.replace(email_password, "[secreto oculto]")
    return mensaje[:500]


def enviar_entrega_email(entrega_id: int, contenido: RenderedEmail) -> None:
    entrega = EntregaComunicacion.objects.get(pk=entrega_id)
    if settings.UNI2_TRANSACTIONAL_EMAIL_MODE == "disabled":
        entrega.estado = EntregaComunicacion.ESTADO_OMITIDA
        entrega.save(update_fields=("estado",))
        return

    entrega.intentos += 1
    entrega.ultimo_intento_en = timezone.now()
    try:
        destinatarios, subject = resolver_entrega_email(
            destino=entrega.destino,
            subject=contenido.subject,
        )
        mensaje = EmailMultiAlternatives(
            subject=subject,
            body=contenido.text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=destinatarios,
        )
        mensaje.attach_alternative(contenido.html, "text/html")
        mensaje.send()
    except Exception as error:  # El backend puede fallar con excepciones propias.
        entrega.estado = EntregaComunicacion.ESTADO_FALLIDA
        entrega.ultimo_error = resumir_error_entrega(error)
        entrega.save(
            update_fields=("estado", "intentos", "ultimo_intento_en", "ultimo_error")
        )
        return

    entrega.estado = EntregaComunicacion.ESTADO_ENVIADA
    entrega.enviado_en = timezone.now()
    entrega.ultimo_error = ""
    entrega.save(
        update_fields=(
            "estado",
            "intentos",
            "ultimo_intento_en",
            "enviado_en",
            "ultimo_error",
        )
    )


def programar_email_transaccional(
    *,
    tipo: str,
    destino: str,
    clave_idempotencia: str,
    origen_entidad: str,
    origen_id: object,
    contexto: dict,
    actor=None,
) -> EntregaComunicacion:
    contenido = render_email(tipo=tipo, contexto=contexto)
    comunicacion, creada = Comunicacion.objects.get_or_create(
        clave_idempotencia=clave_idempotencia,
        defaults={
            "tipo": tipo,
            "alcance": Comunicacion.ALCANCE_INDIVIDUAL,
            "origen_entidad": origen_entidad,
            "origen_id": str(origen_id),
            "creado_por": actor,
        },
    )
    if not creada:
        return comunicacion.entregas.order_by("id").first()

    entrega = EntregaComunicacion.objects.create(
        comunicacion=comunicacion,
        canal=EntregaComunicacion.CANAL_EMAIL,
        destino=destino,
    )
    transaction.on_commit(lambda: enviar_entrega_email(entrega.pk, contenido))
    return entrega
