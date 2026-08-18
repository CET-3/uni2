import re

from django.conf import settings


MEASUREMENT_ID_PATTERN = re.compile(r"G-[A-Z0-9]+")
EMPTY_ANALYTICS_CONTEXT = {
    "google_analytics_measurement_id": "",
    "google_analytics_page_name": "",
}


def google_analytics(request):
    """Expone únicamente datos seguros para medir una vista en Producción."""

    measurement_id = getattr(settings, "GOOGLE_ANALYTICS_MEASUREMENT_ID", "")
    if settings.UNI2_DEPLOYMENT_ENVIRONMENT != "production":
        return EMPTY_ANALYTICS_CONTEXT.copy()
    if not MEASUREMENT_ID_PATTERN.fullmatch(measurement_id):
        return EMPTY_ANALYTICS_CONTEXT.copy()

    resolver_match = getattr(request, "resolver_match", None)
    page_name = resolver_match.view_name if resolver_match else ""
    if not page_name:
        return EMPTY_ANALYTICS_CONTEXT.copy()

    return {
        "google_analytics_measurement_id": measurement_id,
        "google_analytics_page_name": page_name,
    }
