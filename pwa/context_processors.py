from django.conf import settings


def pwa_settings(request):
    """Expone únicamente decisiones PWA necesarias para renderizar el cliente."""

    return {
        "pwa_credential_offline_ttl_days": settings.PWA_CREDENTIAL_OFFLINE_TTL_DAYS,
    }
