from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from config.views import staging_readiness

urlpatterns = [
    path("__staging__/readiness/", staging_readiness, name="staging_readiness"),
    path("", include(("pwa.urls", "pwa"), namespace="pwa")),
    path("admin/", admin.site.urls),
    path("especificacion/", include(("especificacion.urls", "especificacion"), namespace="especificacion")),
    path("", include(("web.urls", "web"), namespace="web")),
    path("", include(("gestion.urls", "gestion"), namespace="gestion")),
    path("", include(("usuarios.urls", "usuarios"), namespace="usuarios")),
    path("asociado/", include(("asociados.urls", "asociados"), namespace="asociados")),
    path("comercio/", include(("comercios.urls", "comercios"), namespace="comercios")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
