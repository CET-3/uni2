# Beneficios con fotos en home — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rediseñar la sección Beneficios de la home para mostrar hasta 3 fotos de comercios por rubro en formato mixer card.

**Architecture:** Agregar campo `foto` al modelo `Comercio`, actualizar el selector `get_rubros_con_comercios()` para prefetch comercios con foto, rediseñar el template `home.html` y agregar estilos CSS.

**Tech Stack:** Django 5, Bootstrap 5, Pillow, pytest-django

## Global Constraints

- Usar pytest y pytest-django para tests
- No React, solo Django Templates + Bootstrap 5
- Nombres de modelo y campos consistentes con la especificación
- El campo foto no es obligatorio (blank=True, null=True)
- Las imágenes se suben a `comercios/`

---

### Task 1: Agregar campo foto al modelo Comercio

**Files:**
- Modify: `comercios/models.py`
- Create: migración
- Test: `comercios/tests/test_models.py`

**Interfaces:**
- Consumes: modelo `Comercio` existente
- Produces: `Comercio.foto` (ImageField, blank=True, null=True, upload_to='comercios/')

- [ ] **Step 1: Escribir test del campo foto**

```python
# comercios/tests/test_models.py
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from comercios.models import Comercio, ActividadComercial


@pytest.mark.django_db
def test_comercio_foto_optional():
    actividad = ActividadComercial.objects.create(nombre="Test")
    comercio = Comercio.objects.create(
        nombre="Test",
        actividad_comercial=actividad,
        beneficio_texto="10% off",
        estado=Comercio.ESTADO_FIRMADO,
        orden=1,
        direccion="Calle 123",
    )
    assert comercio.foto.name is None

    foto = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
    comercio.foto = foto
    comercio.save()
    assert comercio.foto.name is not None
```

- [ ] **Step 2: Agregar ImageField al modelo**

```python
# comercios/models.py — agregar después de flyer_disponible
foto = models.ImageField(
    "foto",
    upload_to="comercios/",
    blank=True,
    null=True,
    help_text="Fotografía del comercio para mostrar en la sección Beneficios de la home.",
)
```

- [ ] **Step 3: Crear migración**

```bash
python manage.py makemigrations comercios
```

- [ ] **Step 4: Correr test para verificar**

```bash
python -m pytest comercios/tests/test_models.py::test_comercio_foto_optional -v
```

- [ ] **Step 5: Commit**

```bash
git add comercios/models.py comercios/migrations/XXXX_comercio_foto.py comercios/tests/test_models.py
git commit -m "feat: agrega campo foto al modelo Comercio"
```

---

### Task 2: Actualizar selector y view de home

**Files:**
- Modify: `comercios/selectors.py`
- Test: `comercios/tests/test_selectors.py`

**Interfaces:**
- Consumes: `Comercio.foto` (nuevo campo)
- Produces: `get_rubros_con_comercios()` ahora retorna `ActividadComercial` con atributo `.comercios_con_foto` (lista de hasta 3 `Comercio` con foto no nula)

- [ ] **Step 1: Escribir test del nuevo comportamiento**

```python
# comercios/tests/test_selectors.py
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from comercios.models import Comercio, ActividadComercial
from comercios.selectors import get_rubros_con_comercios


@pytest.mark.django_db
def test_rubros_con_comercios_incluye_fotos():
    rubro = ActividadComercial.objects.create(nombre="Gastronomía")

    # Comercio sin foto (no debe aparecer en la nube)
    Comercio.objects.create(
        nombre="Sin foto",
        actividad_comercial=rubro,
        beneficio_texto="10% off",
        estado=Comercio.ESTADO_FIRMADO,
        orden=1,
        direccion="Calle 123",
    )

    # 3 comercios con foto
    fotos = []
    for i in range(3):
        foto = SimpleUploadedFile(f"com_{i}.jpg", b"content", content_type="image/jpeg")
        c = Comercio.objects.create(
            nombre=f"Com {i}",
            actividad_comercial=rubro,
            beneficio_texto="10% off",
            estado=Comercio.ESTADO_FIRMADO,
            orden=i + 2,
            direccion=f"Calle {i}",
            foto=foto,
        )
        fotos.append(c)

    qs = get_rubros_con_comercios()
    rubro_result = qs.get(nombre="Gastronomía")
    assert len(rubro_result.comercios_con_foto) == 3


@pytest.mark.django_db
def test_rubros_sin_comercios_firmados_no_aparecen():
    rubro = ActividadComercial.objects.create(nombre="Test")
    # Rubro sin comercios no debería aparecer
    qs = get_rubros_con_comercios()
    assert rubro not in qs


@pytest.mark.django_db
def test_rubro_con_menos_de_3_comercios_con_foto():
    rubro = ActividadComercial.objects.create(nombre="Belleza")
    foto = SimpleUploadedFile("foto.jpg", b"content", content_type="image/jpeg")
    Comercio.objects.create(
        nombre="Único",
        actividad_comercial=rubro,
        beneficio_texto="15% off",
        estado=Comercio.ESTADO_FIRMADO,
        orden=1,
        direccion="Calle 1",
        foto=foto,
    )

    qs = get_rubros_con_comercios()
    rubro_result = qs.get(nombre="Belleza")
    assert len(rubro_result.comercios_con_foto) == 1
```

- [ ] **Step 2: Actualizar get_rubros_con_comercios**

```python
# comercios/selectors.py
from django.db.models import Count, Prefetch, Q


def get_rubros_con_comercios():
    comercios_con_foto = Comercio.objects.filter(
        estado=Comercio.ESTADO_FIRMADO,
        foto__isnull=False,
    ).order_by("orden")[:3]

    return (
        ActividadComercial.objects
        .filter(comercios__estado=Comercio.ESTADO_FIRMADO)
        .annotate(cantidad_comercios=Count("comercios"))
        .prefetch_related(
            Prefetch("comercios", queryset=comercios_con_foto, to_attr="comercios_con_foto")
        )
        .order_by("nombre")
    )
```

- [ ] **Step 3: Correr tests**

```bash
python -m pytest comercios/tests/test_selectors.py -v
```

- [ ] **Step 4: Commit**

```bash
git add comercios/selectors.py comercios/tests/test_selectors.py
git commit -m "feat: actualiza selector de rubros para incluir comercios con foto"
```

---

### Task 3: Rediseñar sección Beneficios en home.html

**Files:**
- Modify: `templates/web/home.html`
- No test necesario (solo HTML/CSS)

**Interfaces:**
- Consumes: `rubros_beneficio` como queryset de `ActividadComercial` con `.comercios_con_foto`
- Produce: HTML rediseñado para la sección Beneficios

- [ ] **Step 1: Reemplazar la grilla de Beneficios en home.html**

Reemplazar el bloque:

```html
<h2 class="h3">Beneficios</h2>
<div class="row g-3">
  {% for rubro in rubros_beneficio %}
    <div class="col-6 col-md-4 col-lg-2">
      <a href="{% url 'web:actividad_comercial_detalle' rubro.pk %}" class="card text-center text-decoration-none h-100">
        <div class="card-body">
          <p class="card-title fw-semibold mb-0">{{ rubro.nombre }}</p>
          <small class="text-muted">{{ rubro.cantidad_comercios }} comercio{{ rubro.cantidad_comercios|pluralize }}</small>
        </div>
      </a>
    </div>
  {% endfor %}
</div>
```

Con:

```html
<h2 class="h3">Beneficios</h2>
<div class="benefit-grid">
  {% for rubro in rubros_beneficio %}
    <a href="{% url 'web:actividad_comercial_detalle' rubro.pk %}" class="benefit-mix-card benefit-mix-card-{{ forloop.counter0|stringformat:'s'|cut:':' }}">
      <span class="logo-cloud">
        {% for comercio in rubro.comercios_con_foto|slice:":3" %}
          {% if forloop.counter == 2 %}
            <span class="logo-dot logo-dot-main">
          {% elif forloop.counter == 1 %}
            <span class="logo-dot logo-dot-left">
          {% else %}
            <span class="logo-dot logo-dot-right">
          {% endif %}
            <img src="{{ comercio.foto.url }}" alt="{{ comercio.nombre }}" loading="lazy">
          </span>
        {% endfor %}
      </span>
      <span class="benefit-rubric">{{ rubro.nombre }}</span>
    </a>
  {% endfor %}
</div>
```

- [ ] **Step 2: Verificar visualmente**

```bash
python manage.py runserver 0.0.0.0:8000
```

- [ ] **Step 3: Commit**

```bash
git add templates/web/home.html
git commit -m "feat: rediseña sección Beneficios con mixer cards y fotos de comercios"
```

---

### Task 4: Agregar estilos CSS

**Files:**
- Modify: `templates/base.html` (linkear CSS)
- Create: `static/css/beneficios.css`

**Interfaces:**
- Consumes: selectors de clase CSS usados en home.html (`.benefit-grid`, `.benefit-mix-card`, `.logo-cloud`, `.logo-dot`, `.benefit-rubric`)
- Produce: archivo CSS y link en base.html

- [ ] **Step 1: Crear static/css/beneficios.css**

```css
/* Beneficios — mixer cards con nube de logos */
.benefit-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.benefit-mix-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  padding: 1.25rem 0.75rem 0.75rem;
  border-radius: 1rem;
  text-decoration: none;
  color: inherit;
  background: linear-gradient(135deg, var(--bs-light, #f8f9fa), #e9ecef);
  min-height: 160px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  overflow: hidden;
}

.benefit-mix-card::before {
  content: '';
  position: absolute;
  inset: 0;
  opacity: 0.08;
  background: radial-gradient(ellipse at 50% 0%, var(--accent-color, #4361ee) 0%, transparent 70%);
  pointer-events: none;
}

.benefit-mix-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  color: inherit;
}

/* Variantes de color para cada card (ciclo de 6) */
.benefit-mix-card-0 { --accent-color: #4361ee; }
.benefit-mix-card-1 { --accent-color: #f72585; }
.benefit-mix-card-2 { --accent-color: #06d6a0; }
.benefit-mix-card-3 { --accent-color: #ffb703; }
.benefit-mix-card-4 { --accent-color: #e36414; }
.benefit-mix-card-5 { --accent-color: #7209b7; }

.logo-cloud {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 90px;
  position: relative;
  margin-bottom: 0.75rem;
}

.logo-dot {
  position: absolute;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
  transition: transform 0.2s ease;
  background: var(--bs-light, #f8f9fa);
}

.logo-dot img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.logo-dot-left {
  left: 5%;
  z-index: 1;
  width: 56px;
  height: 56px;
}

.logo-dot-main {
  left: 50%;
  transform: translateX(-50%);
  z-index: 2;
  width: 72px;
  height: 72px;
}

.logo-dot-right {
  right: 5%;
  z-index: 1;
  width: 56px;
  height: 56px;
}

.benefit-rubric {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--bs-body-color, #212529);
  text-align: center;
  line-height: 1.2;
}

/* Responsive */
@media (max-width: 576px) {
  .benefit-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
  .logo-dot { width: 48px; height: 48px; }
  .logo-dot-main { width: 56px; height: 56px; }
}
```

- [ ] **Step 2: Link CSS en base.html**

```html
<!-- En <head>, después del link a Bootstrap -->
<link rel="stylesheet" href="{% static 'css/beneficios.css' %}">
```

Asegurarse de que `{% load static %}` esté presente en `base.html` (verificar).

- [ ] **Step 3: Commit**

```bash
git add static/css/beneficios.css templates/base.html
git commit -m "feat: agrega estilos para mixer cards de beneficios"
```

---

### Task 5: Verificación final

- [ ] **Step 1: Correr suite de tests completa**

```bash
python -m pytest
```

- [ ] **Step 2: Verificar migraciones aplicadas**

```bash
python manage.py migrate --check
```

- [ ] **Step 3: Verificar que no hay conflictos**

```bash
python manage.py check
```

- [ ] **Step 4: Commit final**

```bash
git add -A
git commit -m "chore: verificación final beneficios home"
```
