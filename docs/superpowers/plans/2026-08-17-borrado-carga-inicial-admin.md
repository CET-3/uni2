# Borrado excepcional de carga inicial en admin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Permitir que solamente los superusuarios borren cursos, asociados y usuarios desde el admin, sin habilitar el borrado de los demás modelos auditados.

**Architecture:** `AuditoriaAdminMixin` mantendrá el bloqueo predeterminado y ofrecerá una bandera de opt-in para administradores concretos. `CursoAdmin`, `AsociadoAdmin` y `Uni2UserAdmin` activarán la bandera; Django conservará sus confirmaciones, cascadas y registro técnico estándar sin crear `EventoAuditoria` de eliminación.

**Tech Stack:** Python, Django Admin, pytest, pytest-django.

## Global Constraints

- Solo `Curso`, `Asociado` y `User` habilitan borrado.
- Solo una cuenta con `is_superuser=True` puede borrar individual o masivamente.
- El resto de `AuditoriaAdminMixin` continúa bloqueando borrados.
- No se registra el borrado en `EventoAuditoria`.
- Los cambios funcionales se documentan en la especificación OKF.

---

### Task 1: Permiso de borrado con opt-in explícito

**Files:**
- Modify: `auditoria/admin_mixins.py`
- Modify: `asociados/admin.py`
- Modify: `usuarios/admin.py`
- Test: `auditoria/tests/test_admin.py`

**Interfaces:**
- Consumes: `ModelAdmin.has_delete_permission(request, obj=None)` de Django.
- Produces: atributo de clase `allow_superuser_delete: bool`, desactivado por defecto, y una implementación de `has_delete_permission()` que exige opt-in y superusuario.

- [ ] **Step 1: Escribir pruebas que fallen**

Agregar una prueba parametrizada para los tres administradores habilitados y otra para un administrador auditado no habilitado:

```python
@pytest.mark.django_db
@pytest.mark.parametrize("model", [Curso, Asociado, get_user_model()])
def test_admin_permite_borrar_modelos_de_carga_inicial_solo_a_superusuario(model):
    superusuario = get_user_model().objects.create_superuser(
        username=f"root_{model._meta.model_name}", password="secreto123"
    )
    operador = get_user_model().objects.create_user(
        username=f"operador_{model._meta.model_name}", password="secreto123", is_staff=True
    )
    model_admin = admin.site._registry[model]

    request_super = SimpleNamespace(user=superusuario)
    request_operador = SimpleNamespace(user=operador)

    assert model_admin.has_delete_permission(request_super) is True
    assert model_admin.has_delete_permission(request_operador) is False


@pytest.mark.django_db
def test_admin_auditado_sin_opt_in_mantiene_borrado_bloqueado():
    superusuario = get_user_model().objects.create_superuser(
        username="root_actividad", password="secreto123"
    )
    model_admin = admin.site._registry[ActividadComercial]

    assert model_admin.has_delete_permission(SimpleNamespace(user=superusuario)) is False
```

- [ ] **Step 2: Ejecutar las pruebas y comprobar el fallo**

Run: `pytest auditoria/tests/test_admin.py -q`

Expected: FAIL porque los tres administradores todavía heredan el bloqueo incondicional.

- [ ] **Step 3: Implementar el permiso mínimo**

En `AuditoriaAdminMixin`, reemplazar el bloqueo incondicional por un opt-in explícito:

```python
class AuditoriaAdminMixin:
    allow_superuser_delete = False

    def has_delete_permission(self, request, obj=None):
        if not self.allow_superuser_delete or not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)
```

Activar `allow_superuser_delete = True` solamente en `CursoAdmin`, `AsociadoAdmin` y `Uni2UserAdmin`.

- [ ] **Step 4: Ejecutar las pruebas focalizadas**

Run: `pytest auditoria/tests/test_admin.py asociados/tests/test_admin.py usuarios/tests/test_admin.py -q`

Expected: PASS.

- [ ] **Step 5: Confirmar el cambio de código**

```bash
git add auditoria/admin_mixins.py asociados/admin.py usuarios/admin.py auditoria/tests/test_admin.py
git commit -m "Habilita borrado inicial para superusuarios"
```

### Task 2: Verificar borrado individual, masivo y relaciones

**Files:**
- Modify: `auditoria/tests/test_admin.py`
- Modify: `asociados/tests/test_admin.py`

**Interfaces:**
- Consumes: administradores registrados en `admin.site._registry` y reglas `CASCADE`/`SET_NULL` de los modelos.
- Produces: cobertura de la disponibilidad de `delete_selected` y de los efectos de borrar `Asociado`, `Curso` y `User`.

- [ ] **Step 1: Escribir pruebas de acciones y relaciones**

Agregar pruebas que comprueben:

```python
assert "delete_selected" in model_admin.get_actions(request_super)
assert "delete_selected" not in model_admin.get_actions(request_operador)
```

Crear un asociado con curso y usuario. Verificar por separado que:

```python
curso.delete()
asociado.refresh_from_db()
assert asociado.curso_actual is None

usuario.delete()
asociado.refresh_from_db()
assert asociado.usuario is None
```

Crear cuotas, pagos, aplicaciones y donaciones con las factories o constructores existentes; borrar el asociado y verificar que no quede ningún registro financiero relacionado.

- [ ] **Step 2: Ejecutar las pruebas para confirmar el comportamiento actual**

Run: `pytest auditoria/tests/test_admin.py asociados/tests/test_admin.py -q`

Expected: PASS para las relaciones declaradas en los modelos. Si una construcción de datos no respeta una restricción vigente, ajustar solamente el fixture de prueba.

- [ ] **Step 3: Confirmar las pruebas de regresión**

```bash
git add auditoria/tests/test_admin.py asociados/tests/test_admin.py
git commit -m "Prueba borrado excepcional de carga inicial"
```

### Task 3: Documentar la excepción operativa

**Files:**
- Modify: `especificacion/reglas/usuarios.md`
- Modify: `especificacion/reglas/asociados.md`
- Modify: `especificacion/arquitectura/trazabilidad.md`

**Interfaces:**
- Consumes: alcance aprobado en `docs/superpowers/specs/2026-08-17-borrado-carga-inicial-admin-design.md`.
- Produces: regla funcional y técnica trazable para futuros mantenedores.

- [ ] **Step 1: Actualizar la especificación**

Documentar que:

- el Administrador de la app puede borrar `Curso`, `Asociado` y `User` desde el admin durante la depuración excepcional de la carga inicial;
- el borrado individual y masivo queda limitado a superusuarios;
- la baja lógica continúa siendo el flujo ordinario para asociados;
- las cascadas y `SET_NULL` son visibles en la confirmación de Django;
- esta excepción no crea `EventoAuditoria`, aunque Django conserva su registro técnico.

- [ ] **Step 2: Revisar formato y consistencia**

Run: `git diff --check`

Expected: sin errores.

- [ ] **Step 3: Ejecutar verificación completa proporcional al cambio**

Run: `pytest auditoria/tests/test_admin.py asociados/tests/test_admin.py usuarios/tests/test_admin.py -q`

Expected: PASS.

- [ ] **Step 4: Confirmar documentación**

```bash
git add especificacion/reglas/usuarios.md especificacion/reglas/asociados.md especificacion/arquitectura/trazabilidad.md
git commit -m "Documenta borrado excepcional de carga inicial"
```
