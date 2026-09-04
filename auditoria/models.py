import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class ModeloTrazable(models.Model):
    creado_en = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        editable=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    modificado_en = models.DateTimeField(auto_now=True)
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        editable=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    class Meta:
        abstract = True


class EventoAuditoria(models.Model):
    ACCION_CREAR = "crear"
    ACCION_MODIFICAR = "modificar"
    ACCION_CAMBIAR_ESTADO = "cambiar_estado"
    ACCION_VINCULAR = "vincular"
    ACCION_DESVINCULAR = "desvincular"
    ACCION_ANULAR = "anular"
    ACCION_ELIMINAR = "eliminar"
    ACCIONES = [
        (ACCION_CREAR, "Crear"),
        (ACCION_MODIFICAR, "Modificar"),
        (ACCION_CAMBIAR_ESTADO, "Cambiar estado"),
        (ACCION_VINCULAR, "Vincular"),
        (ACCION_DESVINCULAR, "Desvincular"),
        (ACCION_ANULAR, "Anular"),
        (ACCION_ELIMINAR, "Eliminar"),
    ]

    ORIGEN_GESTION = "gestion"
    ORIGEN_ADMIN = "admin"
    ORIGEN_IMPORTACION = "importacion"
    ORIGEN_COMANDO = "comando"
    ORIGEN_SISTEMA = "sistema"
    ORIGEN_SITIO_PUBLICO = "sitio_publico"
    ORIGEN_ASOCIADO = "asociado"
    ORIGENES = [
        (ORIGEN_GESTION, "Gestión"),
        (ORIGEN_ADMIN, "Admin de Django"),
        (ORIGEN_IMPORTACION, "Importación"),
        (ORIGEN_COMANDO, "Comando"),
        (ORIGEN_SISTEMA, "Sistema"),
        (ORIGEN_SITIO_PUBLICO, "Sitio público"),
        (ORIGEN_ASOCIADO, "Asociado"),
    ]

    fecha = models.DateTimeField(auto_now_add=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="eventos_auditoria",
    )
    actor_etiqueta = models.CharField(
        "nombre registrado del actor",
        max_length=150,
        help_text=(
            "Copia del nombre visible al registrar el evento. Permanece aunque "
            "la cuenta cambie o deje de existir."
        ),
    )
    accion = models.CharField(max_length=30, choices=ACCIONES)
    entidad = models.CharField(max_length=150)
    objeto_id = models.CharField(max_length=100)
    objeto_descripcion = models.CharField(max_length=255)
    cambios = models.JSONField(default=dict, blank=True)
    motivo = models.CharField(max_length=500, blank=True)
    origen = models.CharField(max_length=30, choices=ORIGENES)
    operacion_id = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        verbose_name = "Evento de auditoría"
        verbose_name_plural = "Eventos de auditoría"
        ordering = ["-fecha", "-id"]
        indexes = [
            models.Index(fields=["entidad", "objeto_id", "fecha"]),
            models.Index(fields=["actor", "fecha"]),
            models.Index(fields=["accion", "fecha"]),
            models.Index(fields=["operacion_id"]),
        ]

    def __str__(self):
        fecha = self.fecha.strftime("%d/%m/%Y %H:%M") if self.fecha else "Sin fecha"
        return f"{fecha} · {self.actor_etiqueta} · {self.get_accion_display()} · {self.objeto_descripcion}"

    def clean(self):
        super().clean()
        if self.accion in {self.ACCION_ANULAR, self.ACCION_ELIMINAR} and not self.motivo.strip():
            raise ValidationError({"motivo": "Esta acción requiere un motivo."})

    def save(self, *args, **kwargs):
        if self.pk and type(self).objects.filter(pk=self.pk).exists():
            raise ValidationError("Los eventos de auditoría no se pueden modificar.")
        self.full_clean()
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Los eventos de auditoría no se pueden eliminar.")
