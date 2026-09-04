from django.conf import settings
from django.db import models


class Comunicacion(models.Model):
    ALCANCE_INDIVIDUAL = "individual"
    ALCANCE_LOTE = "lote"
    ALCANCES = [
        (ALCANCE_INDIVIDUAL, "Individual"),
        (ALCANCE_LOTE, "Lote"),
    ]

    tipo = models.CharField(
        max_length=100,
        help_text="Código estable del hecho que origina la comunicación.",
    )
    alcance = models.CharField(max_length=20, choices=ALCANCES)
    clave_idempotencia = models.CharField(
        "clave de idempotencia",
        max_length=200,
        unique=True,
        help_text="Evita registrar dos veces la misma comunicación.",
    )
    origen_entidad = models.CharField("entidad de origen", max_length=150)
    origen_id = models.CharField("identificador de origen", max_length=100)
    creado_en = models.DateTimeField("creada el", auto_now_add=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="creada por",
        blank=True,
        null=True,
        related_name="comunicaciones_creadas",
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = "Comunicación"
        verbose_name_plural = "Comunicaciones"
        ordering = ["-creado_en", "-id"]
        indexes = [models.Index(fields=["origen_entidad", "origen_id"])]

    def __str__(self):
        return f"{self.tipo} · {self.get_alcance_display()} · {self.creado_en:%d/%m/%Y %H:%M}"

    def get_tipo_display(self):
        from .email_types import EMAIL_TYPES

        email_type = EMAIL_TYPES.get(self.tipo)
        return email_type.label if email_type else self.tipo.replace("_", " ").capitalize()


class EntregaComunicacion(models.Model):
    CANAL_EMAIL = "email"
    CANALES = [(CANAL_EMAIL, "Correo electrónico")]

    ESTADO_PENDIENTE = "pendiente"
    ESTADO_ENVIADA = "enviada"
    ESTADO_FALLIDA = "fallida"
    ESTADO_OMITIDA = "omitida"
    ESTADOS = [
        (ESTADO_PENDIENTE, "Pendiente"),
        (ESTADO_ENVIADA, "Enviada"),
        (ESTADO_FALLIDA, "Fallida"),
        (ESTADO_OMITIDA, "Omitida"),
    ]

    comunicacion = models.ForeignKey(
        Comunicacion,
        related_name="entregas",
        on_delete=models.CASCADE,
    )
    canal = models.CharField(max_length=20, choices=CANALES)
    destino = models.EmailField()
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default=ESTADO_PENDIENTE,
    )
    intentos = models.PositiveIntegerField(default=0)
    ultimo_intento_en = models.DateTimeField("último intento", blank=True, null=True)
    enviado_en = models.DateTimeField("enviada el", blank=True, null=True)
    proveedor_id = models.CharField("identificador del proveedor", max_length=255, blank=True)
    ultimo_error = models.CharField("último error", max_length=500, blank=True)
    creado_en = models.DateTimeField("creada el", auto_now_add=True)

    class Meta:
        verbose_name = "Entrega de comunicación"
        verbose_name_plural = "Entregas de comunicaciones"
        ordering = ["-creado_en", "-id"]
        indexes = [
            models.Index(fields=["estado", "creado_en"]),
            models.Index(fields=["comunicacion", "canal"]),
        ]

    def __str__(self):
        return f"{self.get_canal_display()} · {self.destino} · {self.get_estado_display()}"
