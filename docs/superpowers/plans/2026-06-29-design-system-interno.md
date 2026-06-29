# Design System Interno Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publicar el design system completo como herramienta interna protegida por permiso propio y documentar que las pantallas nuevas deben basarse en él.

**Architecture:** La URL `/design-system/` sigue en la app `web`, pero `DesignSystemView` deja de ser pública y valida `gestion.ver_design_system` con un mixin simple. El showcase vive en `templates/web/design-system.html` y usa assets/CSS versionados en el repo; la navegación lo muestra solo a usuarios con permiso.

**Tech Stack:** Django 5, Django Templates, Bootstrap 5, pytest, pytest-django, permisos Django por `auth.Permission`.

---

## File Structure

- `gestion/permissions.py`: agrega la constante `GESTION_VER_DESIGN_SYSTEM` y su etiqueta.
- `gestion/migrations/0003_alter_permisogestion_options.py`: crea el permiso Django nuevo para `PermisoGestion`.
- `web/views.py`: protege `DesignSystemView` con login + permiso.
- `web/tests/test_views.py`: cubre acceso anónimo, acceso sin permiso y acceso con permiso.
- `templates/includes/navbar.html`: agrega link condicional "Design system".
- `usuarios/tests/test_views.py`: cubre visibilidad del link en navbar.
- `usuarios/management/commands/carga_inicial.py`: asigna el permiso al grupo `Atención de mutual`; administradores lo reciben por `GESTION_PERMISSIONS`.
- `usuarios/tests/test_management_commands.py`: verifica que carga inicial asigne el permiso.
- `templates/web/design-system.html`: porta el HTML completo desde `PAGINA-WEB/design-system.html` y adapta rutas a Django.
- `static/css/uni2-design-system.css`: agrega estilos del showcase que hoy existen en `PAGINA-WEB/style2.css` y faltan en el repo.
- `especificacion/arquitectura/design-system.md`: documenta el visualizador interno y la regla de uso.
- `especificacion/arquitectura/index.md`: enlaza la nueva decisión de arquitectura.
- `especificacion/reglas/usuarios.md`: documenta el nuevo permiso.
- `especificacion/pantallas/index.md`: documenta que las pantallas nuevas/rediseños parten del design system.

---

### Task 1: Permiso y Acceso a `/design-system/`

**Files:**
- Modify: `web/tests/test_views.py`
- Modify: `gestion/permissions.py`
- Modify: `web/views.py`
- Create: `gestion/migrations/0003_alter_permisogestion_options.py`

- [ ] **Step 1: Write failing access tests**

Append to `web/tests/test_views.py`:

```python
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
```

If those imports already exist after editing, keep only one copy. Then append these tests:

```python
@pytest.mark.django_db
def test_design_system_requiere_login(client):
    response = client.get(reverse("web:design-system"))

    assert response.status_code == 302
    assert response.url.startswith("/usuarios/login/")


@pytest.mark.django_db
def test_design_system_requiere_permiso(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="sin_design_system", password="secreto123")
    client.force_login(user)

    response = client.get(reverse("web:design-system"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_design_system_con_permiso_responde(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="con_design_system", password="secreto123")
    permiso = Permission.objects.get(content_type__app_label="gestion", codename="ver_design_system")
    user.user_permissions.add(permiso)
    client.force_login(user)

    response = client.get(reverse("web:design-system"))

    assert response.status_code == 200
    assert "Sistema visual UNI2" in response.content.decode()
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
pytest web/tests/test_views.py::test_design_system_requiere_login web/tests/test_views.py::test_design_system_requiere_permiso web/tests/test_views.py::test_design_system_con_permiso_responde -q
```

Expected: failures because the page is currently public and `ver_design_system` does not exist.

- [ ] **Step 3: Add permission constant**

Modify `gestion/permissions.py`:

```python
GESTION_VER_DESIGN_SYSTEM = "gestion.ver_design_system"
```

Add it after `GESTION_VER_ESPECIFICACION`.

Add to `GESTION_PERMISSION_LABELS` after the specification permission:

```python
(GESTION_VER_DESIGN_SYSTEM, "Puede ver el design system del proyecto"),
```

- [ ] **Step 4: Create migration for the permission**

Create `gestion/migrations/0003_alter_permisogestion_options.py` with:

```python
# Generated manually for the internal design system permission.

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("gestion", "0002_alter_permisogestion_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="permisogestion",
            options={
                "default_permissions": (),
                "managed": False,
                "permissions": [
                    ("ver_dashboard_gestion", "Puede ver el dashboard de gestión"),
                    ("consultar_asociados", "Puede consultar asociados"),
                    ("editar_asociados", "Puede editar asociados"),
                    ("importar_asociados", "Puede importar asociados"),
                    ("exportar_asociados", "Puede exportar asociados"),
                    ("cobrar_cuotas", "Puede cobrar cuotas"),
                    ("ver_deudores", "Puede ver deudores"),
                    ("administrar_periodos_cuota", "Puede administrar períodos de cuota"),
                    ("importar_cuotas_historicas", "Puede importar cuotas históricas"),
                    ("ver_especificacion", "Puede ver la especificación del proyecto"),
                    ("ver_design_system", "Puede ver el design system del proyecto"),
                ],
                "verbose_name": "Permiso de gestión",
                "verbose_name_plural": "Permisos de gestión",
            },
        ),
    ]
```

- [ ] **Step 5: Protect the view**

Modify imports in `web/views.py`:

```python
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
```

Add:

```python
from gestion.permissions import GESTION_VER_DESIGN_SYSTEM, user_has_gestion_permission
```

Replace `DesignSystemView` with:

```python
class VerDesignSystemRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True
    permission_required = GESTION_VER_DESIGN_SYSTEM

    def test_func(self):
        return user_has_gestion_permission(self.request.user, self.permission_required)


class DesignSystemView(VerDesignSystemRequiredMixin, TemplateView):
    template_name = "web/design-system.html"
```

- [ ] **Step 6: Run tests to verify they pass**

Run:

```bash
pytest web/tests/test_views.py::test_design_system_requiere_login web/tests/test_views.py::test_design_system_requiere_permiso web/tests/test_views.py::test_design_system_con_permiso_responde -q
```

Expected: all 3 pass.

- [ ] **Step 7: Commit**

```bash
git add web/tests/test_views.py gestion/permissions.py web/views.py gestion/migrations/0003_alter_permisogestion_options.py
git commit -m "Agregar permiso para ver design system"
```

---

### Task 2: Navbar y Carga Inicial

**Files:**
- Modify: `usuarios/tests/test_views.py`
- Modify: `usuarios/tests/test_management_commands.py`
- Modify: `templates/includes/navbar.html`
- Modify: `usuarios/management/commands/carga_inicial.py`

- [ ] **Step 1: Write failing navbar tests**

Modify import in `usuarios/tests/test_views.py`:

```python
from gestion.permissions import GESTION_COBRAR_CUOTAS, GESTION_VER_DESIGN_SYSTEM
```

Append:

```python
@pytest.mark.django_db
def test_navbar_muestra_design_system_si_tiene_permiso(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="doc_visual", password="secreto123")
    permiso = Permission.objects.get(
        content_type__app_label="gestion",
        codename=GESTION_VER_DESIGN_SYSTEM.split(".", 1)[1],
    )
    user.user_permissions.add(permiso)

    client.force_login(user)
    response = client.get(reverse("web:home"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "Design system" in content
    assert reverse("web:design-system") in content


@pytest.mark.django_db
def test_navbar_no_muestra_design_system_sin_permiso(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="sin_doc_visual", password="secreto123")

    client.force_login(user)
    response = client.get(reverse("web:home"))

    assert response.status_code == 200
    assert "Design system" not in response.content.decode()
```

- [ ] **Step 2: Write failing carga inicial assertion**

Modify import in `usuarios/tests/test_management_commands.py`:

```python
from gestion.permissions import GESTION_COBRAR_CUOTAS, GESTION_IMPORTAR_ASOCIADOS, GESTION_VER_DESIGN_SYSTEM
```

In `test_carga_inicial_crea_usuarios_de_prueba`, after `assert atencion_user.has_perm(GESTION_COBRAR_CUOTAS)`, add:

```python
assert atencion_user.has_perm(GESTION_VER_DESIGN_SYSTEM)
assert admin.has_perm(GESTION_VER_DESIGN_SYSTEM)
```

- [ ] **Step 3: Run tests to verify they fail**

Run:

```bash
pytest usuarios/tests/test_views.py::test_navbar_muestra_design_system_si_tiene_permiso usuarios/tests/test_views.py::test_navbar_no_muestra_design_system_sin_permiso usuarios/tests/test_management_commands.py::test_carga_inicial_crea_usuarios_de_prueba -q
```

Expected: first and carga inicial tests fail because the link and assignment are missing; the negative navbar test may pass.

- [ ] **Step 4: Add navbar link**

In `templates/includes/navbar.html`, after the "Especificación" block, add:

```django
{% if perms.gestion.ver_design_system %}
    <li><a class="dropdown-item" href="{% url 'web:design-system' %}">Design system</a></li>
{% endif %}
```

- [ ] **Step 5: Assign permission in carga inicial**

Modify imports in `usuarios/management/commands/carga_inicial.py`:

```python
GESTION_VER_DESIGN_SYSTEM,
```

Add to `ATENCION_MUTUAL_PERMISSIONS` after `GESTION_VER_ESPECIFICACION`:

```python
GESTION_VER_DESIGN_SYSTEM,
```

- [ ] **Step 6: Run tests to verify they pass**

Run:

```bash
pytest usuarios/tests/test_views.py::test_navbar_muestra_design_system_si_tiene_permiso usuarios/tests/test_views.py::test_navbar_no_muestra_design_system_sin_permiso usuarios/tests/test_management_commands.py::test_carga_inicial_crea_usuarios_de_prueba -q
```

Expected: all pass.

- [ ] **Step 7: Commit**

```bash
git add usuarios/tests/test_views.py usuarios/tests/test_management_commands.py templates/includes/navbar.html usuarios/management/commands/carga_inicial.py
git commit -m "Mostrar design system a usuarios con permiso"
```

---

### Task 3: Port Completo del Showcase Visual

**Files:**
- Modify: `templates/web/design-system.html`
- Modify: `static/css/uni2-design-system.css`
- Test: `web/tests/test_views.py`

- [ ] **Step 1: Add failing content regression test**

Append to `web/tests/test_views.py`:

```python
@pytest.mark.django_db
def test_design_system_porta_secciones_del_showcase(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="showcase_completo", password="secreto123")
    permiso = Permission.objects.get(content_type__app_label="gestion", codename="ver_design_system")
    user.user_permissions.add(permiso)
    client.force_login(user)

    response = client.get(reverse("web:design-system"))

    content = response.content.decode()
    assert response.status_code == 200
    assert "Sistema visual UNI2" in content
    assert "Componentes globales" in content
    assert "Home" in content
    assert "Servicios que suman" in content
    assert "Club de Beneficios" in content
    assert "Operaciones" in content
    assert "Django" in content
    assert "style2.css" not in content
    assert "LOJO_UNI2.png" not in content
    assert "assets/logos/" not in content
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
pytest web/tests/test_views.py::test_design_system_porta_secciones_del_showcase -q
```

Expected: fail because the current template is partial and still does not contain all showcase sections.

- [ ] **Step 3: Replace template with Django-adapted full showcase**

Use `/home/milena/CET3/PAGINA-WEB/design-system.html` as source content, but keep the Django template wrapper:

```django
{% extends "base.html" %}
{% load static %}

{% block title %}Design System | Uni2{% endblock %}

{% block extra_head %}
    {{ block.super }}
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
{% endblock %}

{% block content %}
<div class="page ds-page" id="arriba">
    ...
</div>
{% endblock %}

{% block extra_scripts %}
    {{ block.super }}
    <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
    <script>
        if (window.lucide) lucide.createIcons();
        /* copiar el JS del showcase externo, quitando el setTheme si duplica window.__uni2ToggleTheme */
    </script>
{% endblock %}
```

Adaptations required while copying:

```django
<img src="{% static 'img/logo.png' %}" alt="Logo UNI2">
```

Replace links to `index.html` with:

```django
{% url 'web:home' %}
```

Replace old service links with existing Django URLs only when there is an object-backed URL available in the current template context. Because this showcase has no service objects, use section anchors for visual examples:

```html
href="#servicios"
```

Replace each `assets/logos/...` image cluster with CSS-only logo initials, for example:

```html
<span class="logo-cloud" aria-hidden="true">
    <span class="logo-dot logo-dot-left">AD</span>
    <span class="logo-dot logo-dot-main">LM</span>
    <span class="logo-dot logo-dot-right">LC</span>
</span>
```

Keep these section IDs from the external file:

```html
id="fundamentos"
id="componentes"
id="home"
id="servicios"
id="beneficios"
id="operaciones"
id="django"
```

- [ ] **Step 4: Add missing showcase CSS**

Compare `/home/milena/CET3/PAGINA-WEB/style2.css` with `static/css/uni2-design-system.css`. Copy only classes used by the ported showcase and not already present, especially:

```css
.ds-page
.ds-section
.section-inner
.topbar
.brand
.nav
.ds-more-nav
.cta
.ds-heading
.ds-kicker
.ds-card
.ds-swatch
.hero
.hero-layout
.service-grid
.service-card
.benefit-band
.benefit-mix-card
.logo-cloud
.logo-dot
.ad-carousel
.print-contact
.benefit-list-card
.operation-shell
.ds-filter-chip
.ds-compact-icon
.ds-activity-item
.soon-modal
.theme-toggle-panel
```

Do not paste duplicate `:root` variables that conflict with the existing global design tokens unless the showcase needs a missing alias. If a missing alias is required, add it under the existing `:root` block with a short comment:

```css
/* Aliases used by the internal design-system showcase. */
--azul: var(--primary);
--fondo: var(--bg-alt);
```

- [ ] **Step 5: Run content test**

Run:

```bash
pytest web/tests/test_views.py::test_design_system_porta_secciones_del_showcase -q
```

Expected: pass.

- [ ] **Step 6: Run access tests again**

Run:

```bash
pytest web/tests/test_views.py::test_design_system_requiere_login web/tests/test_views.py::test_design_system_requiere_permiso web/tests/test_views.py::test_design_system_con_permiso_responde web/tests/test_views.py::test_design_system_porta_secciones_del_showcase -q
```

Expected: all pass.

- [ ] **Step 7: Commit**

```bash
git add templates/web/design-system.html static/css/uni2-design-system.css web/tests/test_views.py
git commit -m "Portar showcase interno del design system"
```

---

### Task 4: Especificación OKF

**Files:**
- Create: `especificacion/arquitectura/design-system.md`
- Modify: `especificacion/arquitectura/index.md`
- Modify: `especificacion/reglas/usuarios.md`
- Modify: `especificacion/pantallas/index.md`

- [ ] **Step 1: Create architecture document**

Create `especificacion/arquitectura/design-system.md`:

```markdown
---
type: "Decisión de arquitectura"
title: "Design system interno"
description: "Publicación interna del sistema visual usado para pantallas Uni2."
tags: [mvp, arquitectura, frontend]
timestamp: 2026-06-29T00:00:00-03:00
---

# Design system interno

El design system de Uni2 se sirve en `/design-system/` como una herramienta interna de consulta visual.

Su objetivo es que estudiantes y personas que mantengan el proyecto tengan una referencia común para colores, tipografía, componentes, pantallas públicas, pantallas operativas y patrones Django + Bootstrap.

## Acceso

La vista requiere login y el permiso `gestion.ver_design_system`.

El enlace aparece en el menú desplegable del usuario solo cuando la persona tiene ese permiso. No forma parte de la navegación pública principal.

## Relación con la especificación

La especificación OKF describe reglas, entidades, flujos, pantallas y decisiones. El design system muestra cómo deben verse y componerse las pantallas.

Cuando una pantalla nueva o un rediseño necesita un patrón visual que no existe, primero se debe incorporar o describir el patrón en el design system o en la especificación antes de usarlo en producción.

## Alcance actual

Esta etapa solo publica la referencia visual. No implica migrar automáticamente todas las pantallas existentes.
```

- [ ] **Step 2: Link architecture document**

Add to `especificacion/arquitectura/index.md`:

```markdown
* [Design system interno](design-system.md) - Referencia visual interna para construir pantallas con Django Templates y Bootstrap.
```

- [ ] **Step 3: Document user permission**

Append to `especificacion/reglas/usuarios.md`:

```markdown
## USUARIO-017

El design system del proyecto se sirve en `/design-system/` y requiere el permiso `gestion.ver_design_system`. La navegación muestra el enlace "Design system" solo a usuarios con ese permiso. El permiso está separado de `gestion.ver_especificacion` para mantener explícitas las responsabilidades: una cosa es leer la especificación funcional y otra consultar la referencia visual para construir pantallas.
```

- [ ] **Step 4: Document screen workflow rule**

Append to `especificacion/pantallas/index.md`:

```markdown
## Regla de trabajo visual

Toda pantalla nueva y todo rediseño de una pantalla existente debe partir del [design system interno](../arquitectura/design-system.md).

Antes de crear estilos o estructuras visuales nuevas, revisar si el patrón ya existe en `/design-system/`. Si no existe, documentar el patrón o la decisión antes de aplicarlo en una pantalla operativa.
```

- [ ] **Step 5: Run targeted tests**

Run:

```bash
pytest web/tests/test_views.py::test_design_system_con_permiso_responde usuarios/tests/test_views.py::test_navbar_muestra_design_system_si_tiene_permiso usuarios/tests/test_management_commands.py::test_carga_inicial_crea_usuarios_de_prueba -q
```

Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add especificacion/arquitectura/design-system.md especificacion/arquitectura/index.md especificacion/reglas/usuarios.md especificacion/pantallas/index.md
git commit -m "Documentar uso interno del design system"
```

---

### Task 5: Verificación Final

**Files:**
- No planned edits unless verification exposes a defect.

- [ ] **Step 1: Run focused test set**

Run:

```bash
pytest web/tests/test_views.py usuarios/tests/test_views.py::test_navbar_muestra_design_system_si_tiene_permiso usuarios/tests/test_views.py::test_navbar_no_muestra_design_system_sin_permiso usuarios/tests/test_management_commands.py::test_carga_inicial_crea_usuarios_de_prueba -q
```

Expected: all pass.

- [ ] **Step 2: Run Django checks**

Run:

```bash
python manage.py check
```

Expected: `System check identified no issues`.

- [ ] **Step 3: Inspect final diff**

Run:

```bash
git status --short
git log --oneline -5
```

Expected: only intentional uncommitted workspace files remain; new implementation commits appear at the top.

---

## Self-Review

- Spec coverage: permission, protected URL, menu entry, carga inicial, ported showcase, OKF documentation, and testing are all covered.
- Scope control: no existing screen redesign is included; that remains stage two.
- Placeholder scan: plan contains no TBD/TODO/fill-in placeholders. The only manual copy instruction is bounded to the known external HTML and explicit required adaptations.
- Type consistency: permission name is consistently `gestion.ver_design_system`; codename is `ver_design_system`; URL name remains `web:design-system`.
