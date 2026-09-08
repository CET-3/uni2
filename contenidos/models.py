from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from asociados.models import Curso
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
        help_text=(
            "Nombre de un ícono de Bootstrap Icons, por ejemplo printer o tag. "
            '<a href="https://icons.getbootstrap.com/" target="_blank" rel="noopener">'
            "Elegí el nombre desde la galería de Bootstrap Icons</a>."
        ),
    )
    texto_cta = models.TextField(
        "texto para call to action",
        blank=True,
        help_text="Texto de contacto o acción asociado a esta categoría. Los emails y URLs se convierten en enlaces en la web.",
    )
    imagen_informativa = models.ImageField(
        "imagen informativa",
        upload_to="categorias_productos_servicios/",
        blank=True,
        help_text="Imagen compartida por la categoría, por ejemplo una tabla de talles.",
    )
    titulo_imagen_informativa = models.CharField(
        "título de la imagen informativa",
        max_length=150,
        blank=True,
        help_text="Título público que explica la imagen, por ejemplo Tabla de talles.",
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

    def clean(self):
        super().clean()
        errores = {}
        if self.imagen_informativa and not self.titulo_imagen_informativa:
            errores["titulo_imagen_informativa"] = "Debe indicar un título para la imagen informativa."
        if self.titulo_imagen_informativa and not self.imagen_informativa:
            errores["imagen_informativa"] = "Debe cargar la imagen informativa correspondiente al título."
        if errores:
            raise ValidationError(errores)


class ProductoServicio(models.Model):
    PRECIO_DIFERENCIADO = "diferenciado"
    PRECIO_UNICO = "unico"
    PRECIO_SOLO_ASOCIADOS = "solo_asociados"
    SIN_PRECIO = "sin_precio"

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
        blank=True,
        help_text="Texto público que explica qué incluye.",
    )
    foto = models.ImageField(
        "foto",
        upload_to="productos_servicios/",
        blank=True,
        help_text="Fotografía del producto o servicio para su ficha pública.",
    )
    es_servicio = models.BooleanField(
        "es servicio",
        default=False,
        help_text="Marcar si el ítem es un servicio. Si no se marca, se interpreta como producto.",
    )
    ciclo_destinatario = models.CharField(
        "ciclo destinatario",
        max_length=2,
        choices=Curso.DIVISIONES,
        blank=True,
        help_text="Ciclo escolar al que se dirige el producto o servicio, si corresponde.",
    )
    curso_destinatario = models.CharField(
        "curso destinatario",
        max_length=10,
        blank=True,
        help_text="Año tomado de los cursos cargados, sin distinguir comisión ni turno.",
    )
    precio_asociados = models.DecimalField(
        "precio para asociados",
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Precio vigente para asociados.",
    )
    precio_no_asociados = models.DecimalField(
        "precio para no asociados",
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
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
        indexes = [models.Index(fields=["activo", "orden"])]

    def __str__(self):
        return self.nombre

    def clean(self):
        super().clean()
        errores = {}

        if self.curso_destinatario and not self.ciclo_destinatario:
            errores["curso_destinatario"] = "No puede indicar un curso sin seleccionar el ciclo."

        if self.precio_asociados is not None and self.precio_asociados <= 0:
            errores["precio_asociados"] = "El precio debe ser mayor que cero."
        if self.precio_no_asociados is not None and self.precio_no_asociados <= 0:
            errores["precio_no_asociados"] = "El precio debe ser mayor que cero."

        if self.precio_asociados is None and (not self.es_servicio or self.precio_no_asociados is not None):
            errores["precio_asociados"] = "Debe indicar un precio para asociados."

        if errores:
            raise ValidationError(errores)

    @property
    def tipo_precio(self):
        if self.precio_asociados is None:
            return self.SIN_PRECIO
        if self.precio_no_asociados is None:
            return self.PRECIO_SOLO_ASOCIADOS
        if self.precio_asociados == self.precio_no_asociados:
            return self.PRECIO_UNICO
        return self.PRECIO_DIFERENCIADO


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
