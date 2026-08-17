# Borrado excepcional de períodos de cuota Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Permitir que solamente los superusuarios borren períodos de cuota desde el admin durante la limpieza inicial.

**Architecture:** `PeriodoCuotaAdmin` reutilizará el opt-in `allow_superuser_delete` ya implementado por `AuditoriaAdminMixin`. La relación `Cuota.periodo` conservará `PROTECT`, por lo que no hay cambios de modelo ni migraciones.

**Tech Stack:** Python, Django Admin, pytest, pytest-django.

## Global Constraints

- Solo `is_superuser=True` habilita el borrado individual y masivo.
- `Cuota`, `Pago`, `PagoCuota` y `Donacion` mantienen bloqueado el borrado directo.
- `Cuota.periodo` conserva `on_delete=PROTECT`.
- No se crea un `EventoAuditoria` por esta limpieza.
- La especificación OKF se actualiza junto con el código.

---

### Task 1: Habilitar y documentar el borrado de períodos

**Files:**
- Modify: `cuotas/admin.py`
- Modify: `auditoria/tests/test_admin.py`
- Modify: `cuotas/tests/test_services.py`
- Modify: `especificacion/reglas/cuotas.md`
- Modify: `especificacion/reglas/usuarios.md`
- Modify: `especificacion/arquitectura/trazabilidad.md`

**Interfaces:**
- Consumes: `AuditoriaAdminMixin.allow_superuser_delete: bool` y `ModelAdmin.has_delete_permission(request, obj=None)`.
- Produces: `PeriodoCuotaAdmin.allow_superuser_delete = True` sin cambios de base de datos.

- [ ] **Step 1: Escribir la prueba fallida del permiso**

Incluir `PeriodoCuota` en la parametrización que comprueba el borrado de datos de carga inicial:

```python
@pytest.mark.parametrize("model", [Curso, Asociado, PeriodoCuota, get_user_model()])
def test_admin_permite_borrar_datos_de_carga_inicial_solo_a_superusuario(model):
    ...
```

La prueba existente verifica tanto `has_delete_permission()` como la presencia
de `delete_selected` para el superusuario y su ausencia para el operador.

- [ ] **Step 2: Comprobar el fallo esperado**

Run: `pytest auditoria/tests/test_admin.py::test_admin_permite_borrar_datos_de_carga_inicial_solo_a_superusuario -q`

Expected: FAIL solamente para `PeriodoCuota`, porque su administrador aún no activó el opt-in.

- [ ] **Step 3: Implementar el cambio mínimo**

En `PeriodoCuotaAdmin` agregar:

```python
allow_superuser_delete = True
```

- [ ] **Step 4: Agregar la prueba de integridad `PROTECT`**

Crear un período y una cuota relacionada, e intentar borrar el período:

```python
with pytest.raises(ProtectedError):
    periodo.delete()

assert PeriodoCuota.objects.filter(pk=periodo.pk).exists()
assert Cuota.objects.filter(pk=cuota.pk).exists()
```

La prueba usa un asociado y un ciclo lectivo reales; no reemplaza el ORM con mocks.

- [ ] **Step 5: Actualizar la especificación**

Documentar que `PeriodoCuota` se suma a la limpieza excepcional del
superusuario, que el borrado puede ser individual o masivo, que no genera
`EventoAuditoria` y que los períodos referenciados por cuotas siguen protegidos.

- [ ] **Step 6: Ejecutar verificación focalizada**

Run: `pytest auditoria/tests/test_admin.py cuotas/tests/test_services.py -q`

Expected: PASS.

- [ ] **Step 7: Ejecutar la suite completa y revisar formato**

Run: `git diff --check`

Expected: sin errores.

Run: `pytest -q`

Expected: PASS.

- [ ] **Step 8: Confirmar el cambio**

```bash
git add cuotas/admin.py auditoria/tests/test_admin.py cuotas/tests/test_services.py especificacion/reglas/cuotas.md especificacion/reglas/usuarios.md especificacion/arquitectura/trazabilidad.md
git commit -m "Habilita borrado inicial de periodos de cuota"
```
