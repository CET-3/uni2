from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from config.views import staging_readiness
from web.sitemaps import public_sitemaps
from web.views import robots_txt

urlpatterns = [
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap, {"sitemaps": public_sitemaps}, name="sitemap"),
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
