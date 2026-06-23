# Categoría de Servicio — Vista de Detalle

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Agregar una página por categoría de servicio para ver sus productos desde la home.

**Architecture:** DetailView de `CategoriaProductoServicio` con prefetch de productos activos. URL `/servicios/<pk>/`. La home linkea a esta nueva vista en lugar del anchor roto.

**Tech Stack:** Django + Bootstrap 5

## Global Constraints

- Seguir patrones existentes de `web/views.py` (DetailView, select_related)
- Template extiende `base.html` con Bootstrap 5
- No tocar modelos ni selectors existentes
- TDD: escribir test, verlo fallar, implementar, verlo pasar

---

### Task 1: Test de la nueva vista

**Files:**
- Modify: `web/tests/test_views.py` (agregar tests al final)

- [ ] **Step 1: Agregar tests para categoria_detalle**

Agregar al final de `web/tests/test_views.py`:

```python
@pytest.mark.django_db
def test_categoria_detalle_muestra_sus_productos_activos(client):
    categoria = CategoriaProductoServicio.objects.create(
        nombre="Fotocopias",
        descripcion="Servicios de impresión",
        etiqueta_icono="printer",
        texto_cta="Consultá en la mutual",
        activa=True,
        orden=1,
    )
    ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Fotocopia simple",
        descripcion="ByN",
        precio_asociados=50,
        precio_no_asociados=80,
        activo=True,
        orden=1,
    )
    ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Inactivo",
        descripcion="No visible",
        precio_asociados=100,
        precio_no_asociados=150,
        activo=False,
        orden=2,
    )

    url = reverse("web:categoria_detalle", args=[categoria.pk])
    response = client.get(url)

    assert response.status_code == 200
    assert response.template_name == ["web/categoria_detalle.html"]
    contenido = response.content.decode()
    assert "Fotocopias" in contenido
    assert "Fotocopia simple" in contenido
    assert "Inactivo" not in contenido
    assert "$50,00" in contenido
    assert "Consultá en la mutual" in contenido


@pytest.mark.django_db
def test_categoria_detalle_404_si_inactiva_o_inexistente(client):
    categoria = CategoriaProductoServicio.objects.create(
        nombre="Oculta",
        descripcion="No visible",
        activa=False,
    )

    response = client.get(reverse("web:categoria_detalle", args=[categoria.pk]))
    assert response.status_code == 404

    response = client.get(reverse("web:categoria_detalle", args=[999]))
    assert response.status_code == 404
```

- [ ] **Step 2: Ejecutar para verificar que fallan**

```bash
cd /home/milena/CET3/uni2 && python -m pytest web/tests/test_views.py::test_categoria_detalle_muestra_sus_productos_activos web/tests/test_views.py::test_categoria_detalle_404_si_inactiva_o_inexistente -x -q
```

Expected: FAIL (no existe URL `web:categoria_detalle`)

---

### Task 2: URL, Vista y Template

**Files:**
- Create: `templates/web/categoria_detalle.html`
- Modify: `web/views.py`, `web/urls.py`

- [ ] **Step 1: Agregar vista en web/views.py**

```python
from contenidos.models import CategoriaProductoServicio


class CategoriaProductoServicioDetalleView(DetailView):
    model = CategoriaProductoServicio
    template_name = "web/categoria_detalle.html"
    context_object_name = "categoria"

    def get_queryset(self):
        return CategoriaProductoServicio.objects.filter(activa=True).prefetch_related(
            Prefetch(
                "productos_servicios",
                queryset=ProductoServicio.objects.filter(activo=True).order_by("orden", "nombre"),
            )
        )
```

Necesitás agregar `Prefetch` a los imports de django.db.models:
```python
from django.db.models import Prefetch
```

- [ ] **Step 2: Agregar URL en web/urls.py**

```python
    path("servicios/<int:pk>/", CategoriaProductoServicioDetalleView.as_view(), name="categoria_detalle"),
```

Y agregar el import de la nueva vista.

- [ ] **Step 3: Crear template web/categoria_detalle.html**

```html
{% extends "base.html" %}

{% block title %}{{ categoria.nombre }} | Uni2{% endblock %}

{% block content %}
<nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        <li class="breadcrumb-item"><a href="{% url 'web:home' %}">Inicio</a></li>
        <li class="breadcrumb-item"><a href="{% url 'web:productos_servicios' %}">Productos y servicios</a></li>
        <li class="breadcrumb-item active" aria-current="page">{{ categoria.nombre }}</li>
    </ol>
</nav>

<div class="d-flex align-items-start gap-3 mb-4">
    {% if categoria.etiqueta_icono %}
        <span class="badge text-bg-primary fs-6">{{ categoria.etiqueta_icono }}</span>
    {% endif %}
    <div>
        <h1 class="h2 mb-1">{{ categoria.nombre }}</h1>
        {% if categoria.descripcion %}
            <p class="mb-0 text-secondary">{{ categoria.descripcion }}</p>
        {% endif %}
    </div>
</div>

<div class="row g-3">
    {% for item in categoria.productos_servicios.all %}
        <div class="col-md-6 col-lg-4">
            <div class="card h-100">
                <div class="card-body">
                    <div class="d-flex justify-content-between gap-3">
                        <h2 class="h5 mb-2">{{ item.nombre }}</h2>
                        <span class="badge text-bg-light border">{{ item.es_servicio|yesno:"Servicio,Producto" }}</span>
                    </div>
                    <p class="text-secondary">{{ item.descripcion }}</p>
                    <dl class="row mb-0 small">
                        <dt class="col-6">Asociados</dt>
                        <dd class="col-6 text-end">${{ item.precio_asociados }}</dd>
                        <dt class="col-6">No asociados</dt>
                        <dd class="col-6 text-end">${{ item.precio_no_asociados }}</dd>
                    </dl>
                </div>
            </div>
        </div>
    {% empty %}
        <div class="col-12">
            <p class="text-secondary">No hay productos o servicios cargados en esta categoría.</p>
        </div>
    {% endfor %}
</div>

{% if categoria.texto_cta %}
    <p class="mt-4 mb-0">{{ categoria.texto_cta|urlize }}</p>
{% endif %}
{% endblock %}
```

- [ ] **Step 4: Ejecutar tests para verificar que pasan**

```bash
cd /home/milena/CET3/uni2 && python -m pytest web/tests/test_views.py::test_categoria_detalle_muestra_sus_productos_activos web/tests/test_views.py::test_categoria_detalle_404_si_inactiva_o_inexistente -x -q
```

Expected: PASS

---

### Task 3: Home y listado general

**Files:**
- Modify: `templates/web/home.html`, `templates/web/productos_servicios.html`

- [ ] **Step 1: Home linkea a categoria_detalle**

En `templates/web/home.html`, reemplazar:

```html
<a href="{% url 'web:productos_servicios' %}#{{ categoria.nombre|slugify }}" class="btn btn-outline-primary btn-sm mt-2">
    Ver más
</a>
```

con:

```html
<a href="{% url 'web:categoria_detalle' categoria.pk %}" class="btn btn-outline-primary btn-sm mt-2">
    Ver más
</a>
```

- [ ] **Step 2: Agregar anchors en productos_servicios.html**

En `templates/web/productos_servicios.html`, línea 9, cambiar:

```html
    <section>
```
a:
```html
    <section id="{{ categoria.nombre|slugify }}">
```

- [ ] **Step 3: Correr suite completa**

```bash
cd /home/milena/CET3/uni2 && python -m pytest -q
```

Expected: all tests pass

---

### Task 4: Especificación

**Files:**
- Modify: `especificacion/pantallas/sitio-publico.md`

- [ ] **Step 1: Agregar la nueva pantalla a la especificación**

Agregar sección para la vista `/servicios/<pk>/` en `especificacion/pantallas/sitio-publico.md`, describiendo:
- URL: `/servicios/<pk>/`
- Propósito: ver productos de una categoría específica
- Breadcrumb: Inicio > Productos y servicios > {categoría}
- Contenido: nombre, ícono, descripción, grilla de productos con precios, CTA

- [ ] **Step 2: Verificar que la suite sigue pasando**

```bash
cd /home/milena/CET3/uni2 && python -m pytest -q
```

Expected: all tests pass
