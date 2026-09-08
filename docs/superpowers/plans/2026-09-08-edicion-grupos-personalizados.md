# Edición de grupos — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hacer efectivos `auth.add_group`, `auth.change_group` y `auth.delete_group` para administrar grupos sin restricciones adicionales.

**Architecture:** Se conservará `GroupAdmin` como interfaz y el sistema estándar de permisos de Django como única autorización para crear, editar y borrar. `Uni2GroupAdmin` heredará el alta y la edición; para el borrado delegará directamente en `GroupAdmin` para evitar solo el bloqueo general de `AuditoriaAdminMixin`, que se conserva para auditar los cambios.

**Tech Stack:** Python 3.12, Django, pytest, pytest-django.

## Global Constraints

- Una cuenta con el permiso efectivo `auth.add_group` puede crear grupos.
- Una cuenta con el permiso efectivo `auth.change_group` puede editar cualquier grupo.
- Una cuenta con el permiso efectivo `auth.delete_group` puede borrar grupos.
- No hay grupos protegidos ni excepciones basadas en nombres.
- La decisión funcional debe quedar escrita en `especificacion/reglas/usuarios.md`.
- No se incluyen refactorizaciones ajenas a esta autorización.

---

### Task 1: Delegar la administración de grupos en los permisos estándar

**Files:**
- Modify: `usuarios/tests/test_admin.py`
- Modify: `usuarios/admin.py`
- Modify: `especificacion/reglas/usuarios.md`

**Interfaces:**
- Consumes: `GroupAdmin.has_add_permission(request) -> bool`, `GroupAdmin.has_change_permission(request, obj=None) -> bool` y `GroupAdmin.has_delete_permission(request, obj=None) -> bool`.
- Produces: `Uni2GroupAdmin`, que usa sin excepciones las autorizaciones de alta, edición y borrado de `GroupAdmin`.

- [ ] **Step 1: Escribir la prueba que reproduce el bloqueo incorrecto**

Agregar pruebas que exijan el alta con `auth.add_group` y el borrado con `auth.delete_group`. Reemplazar la prueba que esperaba bloquear los grupos de Uni2 por una prueba parametrizada que exija su edición:

```python
@pytest.mark.django_db
def test_usuario_con_add_group_puede_crear_grupo():
    operador = get_user_model().objects.create_user(
        username="creador-grupos", password="secreto123"
    )
    operador.user_permissions.add(
        Permission.objects.get(content_type__app_label="auth", codename="add_group")
    )
    request = RequestFactory().get("/admin/auth/group/add/")
    request.user = operador

    assert admin.site._registry[Group].has_add_permission(request)


@pytest.mark.django_db
def test_usuario_con_delete_group_puede_borrar_grupo():
    operador = get_user_model().objects.create_user(
        username="borrador-grupos", password="secreto123"
    )
    operador.user_permissions.add(
        Permission.objects.get(content_type__app_label="auth", codename="delete_group")
    )
    grupo = Group.objects.create(name="Grupo para borrar")
    request = RequestFactory().get(f"/admin/auth/group/{grupo.pk}/delete/")
    request.user = operador

    assert admin.site._registry[Group].has_delete_permission(request, grupo)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "nombre_grupo",
    [ADMINISTRADOR_APP_GROUP, ASOCIADO_GROUP, COMERCIO_GROUP],
)
def test_usuario_con_change_group_puede_editar_cualquier_grupo(nombre_grupo):
    operador = get_user_model().objects.create_user(
        username=f"operador-{nombre_grupo}", password="secreto123"
    )
    operador.user_permissions.add(
        Permission.objects.get(content_type__app_label="auth", codename="change_group")
    )
    grupo = Group.objects.get(name=nombre_grupo)
    request = RequestFactory().get(f"/admin/auth/group/{grupo.pk}/change/")
    request.user = operador
    group_admin = admin.site._registry[Group]

    assert group_admin.has_change_permission(request, grupo)
```

Esta prueba falla si reaparece una lista de grupos protegidos o cualquier rechazo adicional al permiso estándar.

- [ ] **Step 2: Ejecutar la prueba y comprobar el fallo actual**

Run:

```bash
DB_ENGINE=sqlite uv run pytest usuarios/tests/test_admin.py::test_usuario_con_add_group_puede_crear_grupo usuarios/tests/test_admin.py::test_usuario_con_delete_group_puede_borrar_grupo usuarios/tests/test_admin.py::test_usuario_con_change_group_puede_editar_cualquier_grupo -q
```

Expected: cinco fallos; uno porque el alta se reserva al superusuario, uno porque el borrado está deshabilitado y tres porque la implementación vigente bloquea esos nombres aunque los permisos están asignados.

- [ ] **Step 3: Eliminar la restricción adicional**

En `usuarios/admin.py`:

- quitar los imports `ASOCIADO_GROUP` y `COMERCIO_GROUP`, que dejan de usarse;
- eliminar `GRUPOS_TECNICOS_PROTEGIDOS`;
- eliminar `Uni2GroupAdmin.has_add_permission` para heredar directamente el comportamiento de `GroupAdmin`;
- eliminar `Uni2GroupAdmin.has_change_permission` para heredar directamente el comportamiento de `GroupAdmin`;
- reemplazar el bloqueo de `Uni2GroupAdmin.has_delete_permission` por una delegación directa a `GroupAdmin.has_delete_permission`, evitando solamente el bloqueo general de `AuditoriaAdminMixin`.

- [ ] **Step 4: Actualizar la especificación funcional**

En `especificacion/reglas/usuarios.md`, dejar explícito que `auth.add_group`, `auth.change_group` y `auth.delete_group` permiten crear, editar y borrar grupos respectivamente, sin excepciones adicionales.

- [ ] **Step 5: Ejecutar las pruebas focalizadas**

Run:

```bash
DB_ENGINE=sqlite uv run pytest usuarios/tests/test_admin.py usuarios/tests/test_permissions.py -q
```

Expected: todas las pruebas pasan.

- [ ] **Step 6: Verificar la suite completa y el alcance**

Run:

```bash
DB_ENGINE=sqlite uv run pytest -q
git diff --check
```

Expected: suite verde y sin errores de whitespace.

- [ ] **Step 7: Crear el commit de implementación**

```bash
git add usuarios/admin.py usuarios/tests/test_admin.py especificacion/reglas/usuarios.md
git commit -m "Respeta permiso de edición de grupos"
```
