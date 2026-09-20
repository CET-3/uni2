from types import SimpleNamespace
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from comercios.models import ActividadComercial, Comercio
from contenidos.models import CategoriaProductoServicio, ProductoServicio


class PublicSitemap(Sitemap):
    def get_urls(self, page=1, site=None, protocol=None):
        if settings.UNI2_SITE_URL:
            origin = urlsplit(settings.UNI2_SITE_URL)
            site = SimpleNamespace(domain=origin.netloc)
            protocol = origin.scheme
        return super().get_urls(page=page, site=site, protocol=protocol)


class PublicStaticSitemap(PublicSitemap):
    def items(self):
        return ("web:home", "web:productos_servicios", "web:comercios")

    def location(self, item):
        return reverse(item)


class PublicModelSitemap(PublicSitemap):
    def __init__(self, queryset):
        self.queryset = queryset

    def items(self):
        return self.queryset.all()


public_sitemaps = {
    "static": PublicStaticSitemap,
    "categories": PublicModelSitemap(CategoriaProductoServicio.objects.filter(activa=True)),
    "products": PublicModelSitemap(ProductoServicio.objects.filter(activo=True, categoria__activa=True)),
    "activities": PublicModelSitemap(ActividadComercial.objects.filter(comercios__estado=Comercio.ESTADO_FIRMADO).distinct()),
    "commerce": PublicModelSitemap(Comercio.objects.filter(estado=Comercio.ESTADO_FIRMADO)),
}
