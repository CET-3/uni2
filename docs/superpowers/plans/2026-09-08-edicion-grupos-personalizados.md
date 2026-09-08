# Edición de grupos — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hacer efectivo `auth.change_group` para editar cualquier grupo sin restricciones adicionales por nombre.

**Architecture:** Se conservará `GroupAdmin` como interfaz y el sistema estándar de permisos de Django como única autorización para editar. `Uni2GroupAdmin` dejará de personalizar `has_change_permission`; el alta y el borrado mantendrán sus reglas actuales.

**Tech Stack:** Python 3.12, Django, pytest, pytest-django.

## Global Constraints

- Una cuenta con el permiso efectivo `auth.change_group` puede editar cualquier grupo.
- No hay grupos protegidos ni excepciones basadas en nombres.
- No se modifica el alta ni el borrado de grupos.
- La decisión funcional debe quedar escrita en `especificacion/reglas/usuarios.md`.
- No se incluyen refactorizaciones ajenas a esta autorización.

---

### Task 1: Delegar completamente la edición en `auth.change_group`

**Files:**
- Modify: `usuarios/tests/test_admin.py`
- Modify: `usuarios/admin.py`
- Modify: `especificacion/reglas/usuarios.md`

**Interfaces:**
- Consumes: `django.contrib.auth.admin.GroupAdmin.has_change_permission(request, obj=None) -> bool`.
- Produces: `Uni2GroupAdmin`, que hereda sin excepciones la autorización de edición de `GroupAdmin`.

- [ ] **Step 1: Escribir la prueba que reproduce el bloqueo incorrecto**

Reemplazar la prueba que esperaba bloquear los grupos de Uni2 por una prueba parametrizada que exija su edición:

```python
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
DB_ENGINE=sqlite uv run pytest usuarios/tests/test_admin.py::test_usuario_con_change_group_puede_editar_cualquier_grupo -q
```

Expected: tres fallos porque la implementación vigente bloquea esos nombres aunque `auth.change_group` esté asignado.

- [ ] **Step 3: Eliminar la restricción adicional**

En `usuarios/admin.py`:

- quitar los imports `ASOCIADO_GROUP` y `COMERCIO_GROUP`, que dejan de usarse;
- eliminar `GRUPOS_TECNICOS_PROTEGIDOS`;
- eliminar `Uni2GroupAdmin.has_change_permission` para heredar directamente el comportamiento de `GroupAdmin`;
- mantener sin cambios `has_add_permission` y `has_delete_permission`.

- [ ] **Step 4: Actualizar la especificación funcional**

En `especificacion/reglas/usuarios.md`, dejar explícito que `auth.change_group` permite editar cualquier grupo y que no existen excepciones adicionales basadas en el nombre del grupo.

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
