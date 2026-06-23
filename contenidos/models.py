from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError

from comercios.models import Comercio


class CategoriaProductoServicio(models.Model):
    nombre = models.CharField(
        "nombre",
        max_length=150,
        unique=True,
        help_text="Nombre visible de la categoría de productos o servicios.",
    )
    descripcion = models.TextField(
        "descripción",
        blank=True,
        help_text="Texto público que explica la categoría.",
    )
    etiqueta_icono = models.CharField(
        "etiqueta de ícono",
        max_length=50,
        blank=True,
        help_text="Etiqueta textual para elegir o representar un ícono, por ejemplo printer.",
    )
    texto_cta = models.TextField(
        "texto para call to action",
        blank=True,
        help_text="Texto de contacto o acción asociado a esta categoría. Los emails y URLs se convierten en enlaces en la web.",
    )
    activa = models.BooleanField(
        "activa",
        default=True,
        help_text="Indica si la categoría se publica en el sitio.",
    )
    orden = models.PositiveIntegerField(
        "orden",
        default=0,
        help_text="Posición usada para ordenar las categorías publicadas.",
    )

    class Meta:
        verbose_name = "Categoría de producto o servicio"
        verbose_name_plural = "Categorías de productos y servicios"
        ordering = ["orden", "nombre"]
        indexes = [models.Index(fields=["activa", "orden"])]

    def __str__(self):
        return self.nombre


class ProductoServicio(models.Model):
    categoria = models.ForeignKey(
        CategoriaProductoServicio,
        on_delete=models.PROTECT,
        related_name="productos_servicios",
        verbose_name="categoría",
        help_text="Categoría pública a la que pertenece este producto o servicio.",
    )
    nombre = models.CharField(
        "nombre",
        max_length=150,
        help_text="Nombre visible del producto o servicio.",
    )
    descripcion = models.TextField(
        "descripción",
        help_text="Texto público que explica qué incluye.",
    )
    es_servicio = models.BooleanField(
        "es servicio",
        default=False,
        help_text="Marcar si el ítem es un servicio. Si no se marca, se interpreta como producto.",
    )
    precio_asociados = models.DecimalField(
        "precio para asociados",
        max_digits=10,
        decimal_places=2,
        help_text="Precio vigente para asociados.",
    )
    precio_no_asociados = models.DecimalField(
        "precio para no asociados",
        max_digits=10,
        decimal_places=2,
        help_text="Precio vigente para personas no asociadas.",
    )
    activo = models.BooleanField(
        "activo",
        default=True,
        help_text="Indica si el producto o servicio se publica en el sitio.",
    )
    orden = models.PositiveIntegerField(
        "orden",
        default=0,
        help_text="Posición usada para ordenar los productos y servicios publicados.",
    )

    class Meta:
        verbose_name = "Producto o servicio"
        verbose_name_plural = "Productos y servicios"
        ordering = ["categoria__orden", "orden", "nombre"]
        constraints = [
            models.UniqueConstraint(fields=["categoria", "nombre"], name="uniq_producto_servicio_por_categoria")
        ]
        indexes = [models.Index(fields=["activo", "orden"])]

    def __str__(self):
        return self.nombre


class Publicidad(models.Model):
    titulo = models.CharField(
        "título",
        max_length=150,
        help_text="Título visible de la publicidad.",
    )
    descripcion = models.TextField(
        "descripción",
        help_text="Texto breve que acompaña la publicidad.",
    )
    etiqueta_principal = models.CharField(
        "etiqueta principal",
        max_length=80,
        help_text="Etiqueta superior de la card, por ejemplo Alimentos o Servicio.",
    )
    etiqueta_secundaria = models.CharField(
        "etiqueta secundaria",
        max_length=80,
        help_text="Texto destacado de la card, por ejemplo 10% OFF o Nuevo.",
    )
    foto = models.ImageField(
        "foto",
        upload_to="publicidades/",
        blank=True,
        help_text="Imagen horizontal recomendada: 1600x900 px, WebP o JPG, menor a 500 KB.",
    )
    producto_servicio = models.ForeignKey(
        ProductoServicio,
        on_delete=models.SET_NULL,
        related_name="publicidades",
        blank=True,
        null=True,
        verbose_name="producto o servicio",
        help_text="Producto o servicio al que apunta la publicidad, si corresponde.",
    )
    comercio = models.ForeignKey(
        Comercio,
        on_delete=models.SET_NULL,
        related_name="publicidades",
        blank=True,
        null=True,
        verbose_name="comercio",
        help_text="Comercio al que apunta la publicidad, si corresponde.",
    )
    activa = models.BooleanField(
        "activa",
        default=True,
        help_text="Indica si la publicidad se muestra en la home.",
    )
    orden = models.PositiveIntegerField(
        "orden",
        default=0,
        help_text="Posición usada para ordenar las publicidades en la home.",
    )

    class Meta:
        verbose_name = "Publicidad"
        verbose_name_plural = "Publicidades"
        ordering = ["orden", "titulo"]
        indexes = [models.Index(fields=["activa", "orden"])]
        constraints = [
            models.CheckConstraint(
                check=models.Q(producto_servicio__isnull=True) | models.Q(comercio__isnull=True),
                name="publicidad_un_solo_destino",
            )
        ]

    def __str__(self):
        return self.titulo

    def clean(self):
        super().clean()
        if self.producto_servicio_id and self.comercio_id:
            raise ValidationError("La publicidad no puede estar vinculada a un producto/servicio y a un comercio a la vez.")

    def get_absolute_url(self):
        if self.producto_servicio_id:
            return reverse("web:producto_servicio_detalle", args=[self.producto_servicio_id])
        if self.comercio_id:
            return reverse("web:comercio_detalle", args=[self.comercio_id])
        return ""
