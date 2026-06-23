from django.db import models


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
