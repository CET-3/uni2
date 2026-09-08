# Edición de grupos personalizados — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hacer efectivo `auth.change_group` para editar grupos personalizados sin habilitar la edición delegada de los tres grupos técnicos de Uni2.

**Architecture:** Se conservará `GroupAdmin` como interfaz y el sistema estándar de permisos de Django como autorización principal. `Uni2GroupAdmin.has_change_permission` agregará solamente una protección por nombre para `Administrador de la app`, `Asociados` y `Comercios` cuando la persona no sea superusuaria.

**Tech Stack:** Python 3.12, Django, pytest, pytest-django.

## Global Constraints

- Los grupos personalizados son administrados por la mutual.
- `auth.change_group` habilita la edición de grupos personalizados.
- `Administrador de la app`, `Asociados` y `Comercios` solo pueden ser editados por un superusuario.
- No se modifica el alta ni el borrado de grupos.
- La decisión funcional debe quedar escrita en `especificacion/reglas/usuarios.md`.
- No se incluyen refactorizaciones ni cambios a la matriz histórica de grupos.

---

### Task 1: Respetar `auth.change_group` en grupos personalizados

**Files:**
- Modify: `usuarios/tests/test_admin.py`
- Modify: `usuarios/admin.py`
- Modify: `especificacion/reglas/usuarios.md`

**Interfaces:**
- Consumes: `django.contrib.auth.admin.GroupAdmin.has_change_permission(request, obj=None) -> bool` y las constantes `ADMINISTRADOR_APP_GROUP`, `ASOCIADO_GROUP`, `COMERCIO_GROUP` de `usuarios.roles`.
- Produces: `Uni2GroupAdmin.has_change_permission(request, obj=None) -> bool`, que conserva la autorización estándar de Django y rechaza únicamente los grupos técnicos para usuarios no superusuarios.

- [ ] **Step 1: Escribir las pruebas que expresan el permiso delegado y la protección técnica**

Agregar a `usuarios/tests/test_admin.py` imports para `Permission`, `Group` y las constantes de los tres grupos técnicos. Incorporar pruebas equivalentes a:

```python
@pytest.mark.django_db
def test_usuario_con_change_group_puede_editar_grupo_personalizado():
    operador = get_user_model().objects.create_user(username="rrhh", password="secreto123")
    operador.user_permissions.add(
        Permission.objects.get(content_type__app_label="auth", codename="change_group")
    )
    grupo = Group.objects.create(name="Recursos Humanos y Coordinación")
    request = RequestFactory().get(f"/admin/auth/group/{grupo.pk}/change/")
    request.user = operador

    group_admin = admin.site._registry[Group]

    assert group_admin.has_change_permission(request, grupo)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "nombre_grupo",
    [ADMINISTRADOR_APP_GROUP, ASOCIADO_GROUP, COMERCIO_GROUP],
)
def test_usuario_con_change_group_no_edita_grupos_tecnicos(nombre_grupo):
    operador = get_user_model().objects.create_user(username=f"rrhh-{nombre_grupo}")
    operador.user_permissions.add(
        Permission.objects.get(content_type__app_label="auth", codename="change_group")
    )
    grupo = Group.objects.get(name=nombre_grupo)
    request = RequestFactory().get(f"/admin/auth/group/{grupo.pk}/change/")
    request.user = operador

    group_admin = admin.site._registry[Group]

    assert not group_admin.has_change_permission(request, grupo)
```

Agregar además una aserción que compruebe que un usuario sin `auth.change_group` no edita un grupo personalizado y que un superusuario sí puede editar los tres grupos técnicos.

- [ ] **Step 2: Ejecutar las pruebas y comprobar el fallo actual**

Run:

```bash
DB_ENGINE=sqlite uv run pytest usuarios/tests/test_admin.py -q
```

Expected: falla la prueba del grupo personalizado porque `Uni2GroupAdmin` devuelve `False` para todo usuario no superusuario; las protecciones técnicas existentes permanecen verdes.

- [ ] **Step 3: Implementar la autorización mínima en el admin**

En `usuarios/admin.py`, importar las tres constantes técnicas y reemplazar el bloqueo general por:

```python
GRUPOS_TECNICOS_PROTEGIDOS = {
    ADMINISTRADOR_APP_GROUP,
    ASOCIADO_GROUP,
    COMERCIO_GROUP,
}


@admin.register(Group)
class Uni2GroupAdmin(AuditoriaAdminMixin, GroupAdmin):
    audit_fields = ("name", "permissions")

    def has_change_permission(self, request, obj=None):
        permitido = super().has_change_permission(request, obj)
        if not permitido or request.user.is_superuser or obj is None:
            return permitido
        return obj.name not in GRUPOS_TECNICOS_PROTEGIDOS
```

Mantener sin cambios `has_add_permission` y `has_delete_permission`.

- [ ] **Step 4: Actualizar la especificación funcional**

En `especificacion/reglas/usuarios.md`, actualizar la descripción de administración de permisos para indicar explícitamente:

- la mutual define y edita sus grupos personalizados;
- una cuenta con `auth.change_group` puede editarlos;
- los grupos `Administrador de la app`, `Asociados` y `Comercios` requieren superusuario;
- el alta y el borrado no cambian en este trabajo.

- [ ] **Step 5: Ejecutar las pruebas focalizadas**

Run:

```bash
DB_ENGINE=sqlite uv run pytest usuarios/tests/test_admin.py usuarios/tests/test_permissions.py -q
```

Expected: todas las pruebas pasan.

- [ ] **Step 6: Verificar formato, diff y alcance**

Run:

```bash
git diff --check
git diff -- usuarios/admin.py usuarios/tests/test_admin.py especificacion/reglas/usuarios.md
```

Expected: sin errores de whitespace; el diff solo contiene la autorización de edición, sus pruebas y la documentación funcional.

- [ ] **Step 7: Crear el commit de implementación**

```bash
git add usuarios/admin.py usuarios/tests/test_admin.py especificacion/reglas/usuarios.md
git commit -m "Permite editar grupos personalizados"
```
