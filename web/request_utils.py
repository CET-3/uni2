import ipaddress

from django.conf import settings


def _normalizar_ip(valor):
    candidato = (valor or "").split(",", 1)[0].strip()
    try:
        return ipaddress.ip_address(candidato).compressed
    except ValueError:
        return ""


def obtener_ip_cliente(request):
    """Devuelve una IP validada desde una fuente confiable para el entorno."""
    candidatos = []
    if settings.UNI2_TRUST_VERCEL_CLIENT_IP:
        candidatos.append(request.META.get("HTTP_X_VERCEL_FORWARDED_FOR", ""))
    candidatos.append(request.META.get("REMOTE_ADDR", ""))

    for candidato in candidatos:
        if ip_normalizada := _normalizar_ip(candidato):
            return ip_normalizada
    return "sin-direccion"
