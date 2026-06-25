# Visualizador de especificación Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task.

**Goal:** Crear una app Django `especificacion` que permita a usuarios staff navegar y leer los archivos Markdown de la especificación desde el navegador.

**Architecture:** Nueva app Django independiente con dos views protegidos por staff. Sin modelos, sin librerías externas. Los archivos `.md` se leen del disco y se muestran en un template con tipografía monospace.

**Tech Stack:** Django, Bootstrap 5, Python stdlib (`os.path`, `pathlib`)

## Global Constraints

- Solo usuarios con `is_staff=True` pueden acceder
- No instalar librerías nuevas
- Seguir el patrón `LoginRequiredMixin` + `UserPassesTestMixin` de las otras apps
- El template extiende `base.html`
- El contenido Markdown se muestra en `<pre>` con clase `font-monospace`

---

### Task 1: Crear la app `especificacion` con views y URLs

**Files:**
- Create: `especificacion/__init__.py`
- Create: `especificacion/apps.py`
- Create: `especificacion/views.py`
- Create: `especificacion/urls.py`
- Create: `especificacion/templates/especificacion/archivo.html`
- Modify: `config/urls.py` (agregar include)
- Modify: `config/settings/base.py` o el que corresponda (agregar app a INSTALLED_APPS)

**Interfaces:**
- Consumes: `config/urls.py` tiene espacio para nuevas apps
- Produces: namespace `especificacion` con URLs `especificacion:indice` y `especificacion:archivo`

- [ ] **Step 1: Crear `especificacion/__init__.py`**

```python

```

- [ ] **Step 2: Crear `especificacion/apps.py`**

```python
from django.apps import AppConfig


class EspecificacionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "especificacion"
    verbose_name = "Especificación"
```

- [ ] **Step 3: Crear `especificacion/views.py`**

```python
from pathlib import Path

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.views.generic import TemplateView


BASE_ESPECIFICACION = Path(settings.BASE_DIR) / "especificacion"


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return self.request.user.is_staff


class IndiceView(StaffRequiredMixin, TemplateView):
    template_name = "especificacion/archivo.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ruta_md = BASE_ESPECIFICACION / "index.md"
        context["contenido_md"] = ruta_md.read_text(encoding="utf-8")
        context["titulo"] = "Especificación - Índice"
        context["ruta_relativa"] = "index.md"
        return context


class ArchivoView(StaffRequiredMixin, TemplateView):
    template_name = "especificacion/archivo.html"

    def get(self, request, *args, **kwargs):
        ruta = kwargs.get("ruta", "")
        if not ruta.endswith(".md"):
            ruta = f"{ruta}.md"

        archivo = (BASE_ESPECIFICACION / ruta).resolve()

        # Path traversal protection
        try:
            archivo.relative_to(BASE_ESPECIFICACION.resolve())
        except ValueError:
            raise Http404("Archivo no válido")

        if not archivo.exists() or not archivo.is_file():
            raise Http404("Archivo no encontrado")

        contenido = archivo.read_text(encoding="utf-8")
        context = self.get_context_data(contenido_md=contenido, titulo=f"Especificación - {ruta}", ruta_relativa=ruta)
        return self.render_to_response(context)
```

- [ ] **Step 4: Crear `especificacion/urls.py`**

```python
from django.urls import path

from .views import ArchivoView, IndiceView

app_name = "especificacion"

urlpatterns = [
    path("", IndiceView.as_view(), name="indice"),
    path("<path:ruta>/", ArchivoView.as_view(), name="archivo"),
]
```

- [ ] **Step 5: Crear template `especificacion/templates/especificacion/archivo.html`**

```html
{% extends "base.html" %}
{% block title %}{{ titulo }}{% endblock %}
{% block content %}
<div class="card surface-card">
    <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-2">
            <small class="text-muted">{{ ruta_relativa }}</small>
            <a href="{% url 'especificacion:indice' %}" class="btn btn-outline-primary btn-sm">← Índice</a>
        </div>
        <pre class="font-monospace" style="font-size:0.88rem; white-space:pre-wrap; word-break:break-word; background:#f8f9fa; padding:1rem; border-radius:0.5rem; max-height:80vh; overflow-y:auto;">{{ contenido_md }}</pre>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 6: Modificar `config/urls.py` para incluir la nueva app**

```python
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("especificacion/", include(("especificacion.urls", "especificacion"), namespace="especificacion")),
    path("", include(("web.urls", "web"), namespace="web")),
    path("", include(("gestion.urls", "gestion"), namespace="gestion")),
    path("", include(("usuarios.urls", "usuarios"), namespace="usuarios")),
    path("asociado/", include(("asociados.urls", "asociados"), namespace="asociados")),
    path("comercio/", include(("comercios.urls", "comercios"), namespace="comercios")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

- [ ] **Step 7: Agregar app a INSTALLED_APPS en `config/settings/base.py`**

Agregar `"especificacion"` al final de la lista, después de `"contenidos",`:

```python
    "contenidos",
    "especificacion",
]

- [ ] **Step 8: Verificar que funciona**

Run: `python manage.py show_urls | grep especificacion`
Expected: muestra las URLs de especificacion

Run: `python manage.py check`
Expected: "System check identified no issues (0 silenced)."

- [ ] **Step 9: Commit**

```bash
git add especificacion/ config/urls.py
git commit -m "feat: app especificacion con lector de markdown para staff"
```

---

### Task 2: Agregar link en navbar para staff

**Files:**
- Modify: `templates/includes/navbar.html`

**Interfaces:**
- Consumes: `user.is_staff` del context processor existente
- Produces: link visible en navbar para staff

- [ ] **Step 1: Agregar link en navbar dentro del bloque de authenticated user**

```html
{% if es_staff %}
    <li><a class="dropdown-item" href="{% url 'especificacion:indice' %}">Especificación</a></li>
{% endif %}
```

Ubicarlo en `templates/includes/navbar.html` justo antes del `<hr class="dropdown-divider">` (línea 39).

- [ ] **Step 2: Commit**

```bash
git add templates/includes/navbar.html
git commit -m "feat: link a especificacion en navbar para staff"
```

---

### Task 3: Tests

**Files:**
- Create: `especificacion/tests/__init__.py`
- Create: `especificacion/tests/test_views.py`

- [ ] **Step 1: Crear `especificacion/tests/__init__.py`**

```python

```

- [ ] **Step 2: Crear `especificacion/tests/test_views.py`**

```python
import pytest
from django.contrib.auth.models import User
from django.urls import reverse


@pytest.mark.django_db
class TestEspecificacionIndice:
    def test_indice_redirect_si_no_autenticado(self, client):
        response = client.get(reverse("especificacion:indice"))
        assert response.status_code in (302, 403)

    def test_indice_redirect_si_no_staff(self, client):
        user = User.objects.create_user(username="test", password="test")
        client.force_login(user)
        response = client.get(reverse("especificacion:indice"))
        assert response.status_code in (302, 403)

    def test_indice_ok_para_staff(self, client):
        user = User.objects.create_user(username="staff", password="test", is_staff=True)
        client.force_login(user)
        response = client.get(reverse("especificacion:indice"))
        assert response.status_code == 200
        assert "Especificación Uni2" in response.content.decode()


@pytest.mark.django_db
class TestEspecificacionArchivo:
    def test_archivo_valido_ok(self, client):
        user = User.objects.create_user(username="staff", password="test", is_staff=True)
        client.force_login(user)
        response = client.get(reverse("especificacion:archivo", kwargs={"ruta": "proyecto/index.md"}))
        assert response.status_code == 200

    def test_archivo_inexistente_404(self, client):
        user = User.objects.create_user(username="staff", password="test", is_staff=True)
        client.force_login(user)
        response = client.get(reverse("especificacion:archivo", kwargs={"ruta": "no-existe.md"}))
        assert response.status_code == 404

    def test_archivo_path_traversal_rechazado(self, client):
        user = User.objects.create_user(username="staff", password="test", is_staff=True)
        client.force_login(user)
        response = client.get(reverse("especificacion:archivo", kwargs={"ruta": "../manage.py"}))
        assert response.status_code == 404
```

- [ ] **Step 3: Ejecutar tests**

Run: `pytest especificacion/tests/ -v`
Expected: todos los tests pasan

- [ ] **Step 4: Commit**

```bash
git add especificacion/tests/
git commit -m "test: tests del visualizador de especificacion"
```
