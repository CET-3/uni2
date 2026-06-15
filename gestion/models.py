from django.db import models

from .permissions import GESTION_PERMISSION_LABELS


class PermisoGestion(models.Model):
    class Meta:
        managed = False
        default_permissions = ()
        permissions = [
            (permission.split(".", 1)[1], label)
            for permission, label in GESTION_PERMISSION_LABELS
        ]
        verbose_name = "Permiso de gestión"
        verbose_name_plural = "Permisos de gestión"
