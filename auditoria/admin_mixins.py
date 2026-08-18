from .models import EventoAuditoria
from .services import construir_cambios, registrar_evento


class AuditoriaAdminMixin:
    audit_fields = ()
    audit_inline_fields = {}
    allow_superuser_delete = False

    def preparar_objeto_para_auditoria(self, request, obj):
        """Hook para ajustes derivados que deben formar parte del mismo evento."""

        return None

    def _audit_snapshot(self, obj, fields):
        snapshot = {}
        for field_name in fields:
            field = obj._meta.get_field(field_name)
            if field.many_to_many:
                snapshot[field_name] = list(getattr(obj, field_name).order_by("pk")) if obj.pk else []
            else:
                snapshot[field_name] = getattr(obj, field_name)
        return snapshot

    def _audit_persisted_snapshot(self, obj, fields):
        if not obj.pk:
            return {field: None for field in fields}
        persisted = type(obj).objects.filter(pk=obj.pk).first()
        if persisted is None:
            return {field: None for field in fields}
        return self._audit_snapshot(persisted, fields)

    def _audit_saved_object(self, *, request, obj, fields, previous, created):
        current = self._audit_snapshot(obj, fields)
        changes = construir_cambios(anteriores=previous, nuevos=current, campos=fields)
        if not changes:
            return
        registrar_evento(
            actor=request.user,
            accion=EventoAuditoria.ACCION_CREAR if created else EventoAuditoria.ACCION_MODIFICAR,
            entidad=obj._meta.label,
            objeto_id=obj.pk,
            objeto_descripcion=str(obj),
            cambios=changes,
            origen=EventoAuditoria.ORIGEN_ADMIN,
        )

    def save_model(self, request, obj, form, change):
        obj._audit_previous = self._audit_persisted_snapshot(obj, self.audit_fields)
        obj._audit_created = not change
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        self.preparar_objeto_para_auditoria(request, obj)
        self._audit_saved_object(
            request=request,
            obj=obj,
            fields=self.audit_fields,
            previous=obj._audit_previous,
            created=obj._audit_created,
        )

    def save_formset(self, request, form, formset, change):
        fields = self.audit_inline_fields.get(formset.model)
        if not fields:
            return super().save_formset(request, form, formset, change)

        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for obj in instances:
            created = obj.pk is None
            previous = self._audit_persisted_snapshot(obj, fields)
            obj.save()
            self._audit_saved_object(
                request=request,
                obj=obj,
                fields=fields,
                previous=previous,
                created=created,
            )
        formset.save_m2m()

    def has_delete_permission(self, request, obj=None):
        if not self.allow_superuser_delete or not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)

    def get_deleted_objects(self, objs, request):
        deleted_objects, model_count, perms_needed, protected = super().get_deleted_objects(
            objs,
            request,
        )
        if self.allow_superuser_delete and request.user.is_superuser:
            perms_needed.clear()
        return deleted_objects, model_count, perms_needed, protected
