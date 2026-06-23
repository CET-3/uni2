# ActividadComercialDetalleView Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a dedicated page per `ActividadComercial` showing its firmado comercios, reachable from home's Beneficios section.

**Architecture:** `DetailView` on `ActividadComercial` with `prefetch_related` for filtered comercios, reusing the same pattern as `CategoriaProductoServicioDetalleView`.

**Tech Stack:** Django DetailView, Bootstrap 5 templates, pytest

## Global Constraints

- No model changes
- No selector changes
- Follow the same pattern as `CategoriaProductoServicioDetalleView`
- Template names use snake_case: `actividadcomercial_detalle.html`

---
### Task 1: Tests

**Files:**
- Modify: `web/tests/test_views.py` (add 2 tests at end)

**Interfaces:**
- URL name: `web:actividad_comercial_detalle` with pk arg
- Template: `web/actividadcomercial_detalle.html`
- Context object: `actividad_comercial`

- [ ] **Step 1: Write failing tests**

Agregar al final de `web/tests/test_views.py`:

```python
@pytest.mark.django_db
def test_actividad_comercial_detalle_muestra_sus_comercios_firmados(client):
    actividad = ActividadComercial.objects.create(nombre="Gastronomía")
    Comercio.objects.create(
        nombre="Parrilla Don Pancho",
        direccion="Mitre 100",
        actividad_comercial=actividad,
        beneficio_texto="10% de descuento",
        estado=Comercio.ESTADO_FIRMADO,
        orden=1,
    )
    Comercio.objects.create(
        nombre="Lo de Carlitos",
        direccion="Belgrano 200",
        actividad_comercial=actividad,
        beneficio_texto="2x1 en milanesas",
        estado=Comercio.ESTADO_FIRMADO,
        orden=2,
    )
    Comercio.objects.create(
        nombre="No Visible",
        direccion="Oculta 300",
        actividad_comercial=actividad,
        beneficio_texto="No publicado",
        estado=Comercio.ESTADO_PENDIENTE,
        orden=3,
    )

    url = reverse("web:actividad_comercial_detalle", args=[actividad.pk])
    response = client.get(url)

    assert response.status_code == 200
    assert response.template_name == ["web/actividadcomercial_detalle.html"]
    assert response.context["actividad_comercial"].nombre == "Gastronomía"
    contenido = response.content.decode()
    assert "Gastronomía" in contenido
    assert "Parrilla Don Pancho" in contenido
    assert "10% de descuento" in contenido
    assert "Lo de Carlitos" in contenido
    assert "No Visible" not in contenido


@pytest.mark.django_db
def test_actividad_comercial_detalle_404_sin_comercios_o_inexistente(client):
    actividad = ActividadComercial.objects.create(nombre="Vacía")

    response = client.get(reverse("web:actividad_comercial_detalle", args=[actividad.pk]))
    assert response.status_code == 404

    response = client.get(reverse("web:actividad_comercial_detalle", args=[999]))
    assert response.status_code == 404
```

Necesitás agregar el import de `ActividadComercial` si no está:
```python
from comercios.models import ActividadComercial, Comercio
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest web/tests/test_views.py::test_actividad_comercial_detalle_muestra_sus_comercios_firmados web/tests/test_views.py::test_actividad_comercial_detalle_404_sin_comercios_o_inexistente -x -q`
Expected: FAIL with `NoReverseMatch` for `'actividad_comercial_detalle'`

- [ ] **Step 3: Stage changes without committing**

```bash
git add web/tests/test_views.py
```

---
### Task 2: URL, Vista y Template

**Files:**
- Create: `templates/web/actividadcomercial_detalle.html`
- Modify: `web/views.py`, `web/urls.py`

**Interfaces:**
- Consumes: URL name `web:actividad_comercial_detalle`, template `web/actividadcomercial_detalle.html`
- Produces: `ActividadComercialDetalleView` in `web/views.py`, URL in `web/urls.py`

- [ ] **Step 1: Agregar vista en web/views.py**

```python
from comercios.models import ActividadComercial


class ActividadComercialDetalleView(DetailView):
    model = ActividadComercial
    template_name = "web/actividadcomercial_detalle.html"
    context_object_name = "actividad_comercial"

    def get_queryset(self):
        return ActividadComercial.objects.filter(
            comercios__estado=Comercio.ESTADO_FIRMADO,
        ).distinct().prefetch_related(
            Prefetch(
                "comercios",
                queryset=Comercio.objects.filter(estado=Comercio.ESTADO_FIRMADO).order_by("orden", "nombre"),
            )
        )
```

`Prefetch` ya está importado (de la feature anterior). Si no, agregar:
```python
from django.db.models import Prefetch
```

- [ ] **Step 2: Agregar URL en web/urls.py**

Import:
```python
    ActividadComercialDetalleView,
```

URL:
```python
    path("actividades-comerciales/<int:pk>/", ActividadComercialDetalleView.as_view(), name="actividad_comercial_detalle"),
```

- [ ] **Step 3: Crear template**

`templates/web/actividadcomercial_detalle.html`:

```html
{% extends "base.html" %}

{% block title %}{{ actividad_comercial.nombre }} | Uni2{% endblock %}

{% block content %}
<nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        <li class="breadcrumb-item"><a href="{% url 'web:home' %}">Inicio</a></li>
        <li class="breadcrumb-item"><a href="{% url 'web:comercios' %}">Comercios</a></li>
        <li class="breadcrumb-item active" aria-current="page">{{ actividad_comercial.nombre }}</li>
    </ol>
</nav>

<h1 class="h2 mb-4">{{ actividad_comercial.nombre }}</h1>

<div class="d-flex flex-column gap-3">
    {% for comercio in actividad_comercial.comercios.all %}
        <article class="card">
            <div class="card-body">
                <h2 class="h5">{{ comercio.nombre }}</h2>
                <p class="mb-1 text-secondary">{{ comercio.direccion }}</p>
                {% if comercio.beneficio_texto %}
                    <p class="mb-1"><strong>Beneficio:</strong> {{ comercio.beneficio_texto }}</p>
                {% endif %}
                {% if comercio.telefono %}
                    <p class="mb-1"><strong>Teléfono:</strong> {{ comercio.telefono }}</p>
                {% endif %}
                {% if comercio.url_presencia_web %}
                    <a href="{{ comercio.url_presencia_web }}" target="_blank" rel="noopener noreferrer">Presencia web</a>
                {% endif %}
            </div>
        </article>
    {% empty %}
        <p class="text-secondary">No hay comercios adheridos en esta categoría.</p>
    {% endfor %}
</div>

<a href="{% url 'web:comercios' %}" class="btn btn-outline-secondary mt-4">← Todos los comercios</a>
{% endblock %}
```

- [ ] **Step 4: Ejecutar tests para verificar que pasan**

Run: `python -m pytest web/tests/test_views.py::test_actividad_comercial_detalle_muestra_sus_comercios_firmados web/tests/test_views.py::test_actividad_comercial_detalle_404_sin_comercios_o_inexistente -x -q`
Expected: PASS

- [ ] **Step 5: Stage changes**

```bash
git add web/views.py web/urls.py templates/web/actividadcomercial_detalle.html
```

---
### Task 3: Home link

**Files:**
- Modify: `templates/web/home.html`

**Interfaces:**
- Consumes: URL name `web:actividad_comercial_detalle`

- [ ] **Step 1: Cambiar link en home.html**

En `templates/web/home.html`, reemplazar:

```html
                        <a href="{% url 'web:comercios' %}" class="card h-100 text-center text-decoration-none">
```

con:

```html
                        <a href="{% url 'web:actividad_comercial_detalle' rubro.pk %}" class="card h-100 text-center text-decoration-none">
```

(Es la línea ~60 del archivo, dentro del loop `{% for rubro in rubros_beneficio %}`)

- [ ] **Step 2: Correr suite completa**

Run: `python -m pytest -q`
Expected: all tests pass

- [ ] **Step 3: Stage changes**

```bash
git add templates/web/home.html
```

---
### Task 4: Especificación

**Files:**
- Modify: `especificacion/pantallas/sitio-publico.md`

- [ ] **Step 1: Agregar la nueva pantalla a la especificación**

En `especificacion/pantallas/sitio-publico.md`, después de la entrada de Productos y servicios, agregar:

```markdown
  - Actividad comercial detalle (`/actividades-comerciales/<pk>/`): muestra nombre de la actividad comercial y listado de sus comercios firmados con dirección, beneficio, teléfono y presencia web. Incluye breadcrumb (Inicio > Comercios > {actividad comercial}) y botón de vuelta al listado general.
- Comercios: listado público vertical de comercios con estado `Firmado`, ordenado por `orden`.
```

y mover la línea existente de Comercios para que quede después de la nueva entrada.

- [ ] **Step 2: Verificar que la suite sigue pasando**

Run: `python -m pytest -q`
Expected: all tests pass

- [ ] **Step 3: Stage and commit all**

```bash
git add -A
git commit -m "Agrega vista detalle de actividad comercial

- ActividadComercialDetalleView con prefetch de comercios firmados
- URL /actividades-comerciales/<pk>/ con breadcrumb y template Bootstrap 5
- Home linkea a actividad_comercial_detalle en vez de lista general
- Especificación actualizada con la nueva pantalla
- Tests: muestra comercios firmados, 404 si vacía o inexistente"
```

---
