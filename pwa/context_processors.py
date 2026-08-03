from django.conf import settings


def pwa_settings(request):
    """Expone únicamente decisiones PWA necesarias para renderizar el cliente."""

    icon_directory = settings.PWA_ICON_DIRECTORY
    return {
        "pwa_credential_offline_ttl_days": settings.PWA_CREDENTIAL_OFFLINE_TTL_DAYS,
        "pwa_private_data_epoch": settings.PWA_PRIVATE_DATA_EPOCH,
        "pwa_app_name": settings.PWA_APP_NAME,
        "pwa_short_name": settings.PWA_SHORT_NAME,
        "pwa_theme_color": settings.PWA_THEME_COLOR,
        "pwa_theme_color_light": settings.PWA_THEME_COLOR_LIGHT,
        "pwa_theme_color_dark": settings.PWA_THEME_COLOR_DARK,
        "pwa_favicon_path": f"{icon_directory}/favicon-32.png",
        "pwa_icon_192_path": f"{icon_directory}/icon-192.png",
        "pwa_apple_touch_icon_path": f"{icon_directory}/apple-touch-icon-180.png",
        "uni2_deployment_environment": settings.UNI2_DEPLOYMENT_ENVIRONMENT,
        "uni2_environment_label": settings.UNI2_ENVIRONMENT_LABEL,
        "uni2_environment_short_label": settings.UNI2_ENVIRONMENT_SHORT_LABEL,
    }
