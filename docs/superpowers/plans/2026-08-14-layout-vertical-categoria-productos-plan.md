# Layout vertical y ciclos de categorías Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Presentar cada categoría con título y descripción arriba, productos debajo agrupados primero por ciclo y luego por curso, y un selector de ciclos accesible en mobile.

**Architecture:** `contenidos/selectors.py` entregará una estructura jerárquica explícita para que la vista no contenga reglas de agrupación. La plantilla de categoría usará un flujo vertical y delegará el renderizado repetido de tablas en un partial; un JavaScript progresivo mostrará un ciclo por vez solamente en mobile.

**Tech Stack:** Django, Templates Django, Bootstrap 5, CSS, JavaScript sin dependencias, pytest y pytest-django.

## Global Constraints

- El cambio de layout afecta solamente a `/servicios/<pk>/`; la ficha individual conserva dos columnas.
- Los productos generales permanecen visibles fuera del selector de ciclos.
- En desktop se muestran todos los ciclos; en mobile se alternan y Ciclo Básico queda seleccionado inicialmente cuando existe.
- Si existe un solo ciclo, no se presenta el selector mobile.
- Sin JavaScript se muestran todos los ciclos.
- No modificar modelos, migraciones ni reglas de precio.
- Conservar encabezados por tipo de ítem, precios alineados a la derecha y omisión de columnas para grupos sin precio.
- Actualizar la especificación OKF en el mismo trabajo.
- Preservar cambios ajenos presentes en el árbol de trabajo.

---

### Task 1: Estructura jerárquica del catálogo público

**Files:**
- Modify: `contenidos/selectors.py`
- Modify: `contenidos/tests/test_selectors.py`
- Modify: `web/tests/test_views.py`

**Interfaces:**
- Produces: `get_bloques_productos_publicos(categoria) -> dict` con claves `generales`, `ciclos` y `mostrar_selector_ciclos`.
- `generales` es `None` o `{"grupos_precio": list[dict]}`.
- Cada ciclo expone `codigo`, `slug`, `titulo`, `etiqueta_corta` y `grupos`.
- Cada grupo de ciclo expone `titulo` y `grupos_precio`.
- Cada grupo de precio conserva `tipo_precio`, `etiqueta_items` e `items`.

- [ ] **Step 1: Reemplazar las expectativas planas por pruebas fallidas de la jerarquía**

En `contenidos/tests/test_selectors.py`, crear un caso con producto general,
producto para todo CB, productos de `1ro` y `2do` CB, y producto de `1ro` CS.
La expectativa principal debe ser:

```python
catalogo = get_bloques_productos_publicos(categoria)

assert catalogo["generales"]["grupos_precio"][0]["items"][0].nombre == "General"
assert [ciclo["codigo"] for ciclo in catalogo["ciclos"]] == ["CB", "CS"]
assert [grupo["titulo"] for grupo in catalogo["ciclos"][0]["grupos"]] == [
    "Para todo el ciclo",
    "1.º C.B.",
    "2.º C.B.",
]
assert [grupo["titulo"] for grupo in catalogo["ciclos"][1]["grupos"]] == ["1.º C.S."]
assert catalogo["mostrar_selector_ciclos"] is True
```

Actualizar las pruebas existentes para consultar `catalogo["generales"]` o
los grupos internos del ciclo correspondiente. Agregar un caso con un único
ciclo que compruebe `mostrar_selector_ciclos is False` y otro sin productos
que espere `{"generales": None, "ciclos": [], "mostrar_selector_ciclos": False}`.

- [ ] **Step 2: Ejecutar las pruebas del selector y comprobar el fallo**

Run: `pytest contenidos/tests/test_selectors.py -q`

Expected: FAIL porque el selector todavía devuelve una lista plana.

- [ ] **Step 3: Implementar la agrupación mínima**

Extraer `_agrupar_por_precio(items)` para construir los grupos actuales y
mantener `_etiqueta_items()`. Hacer que `get_bloques_productos_publicos()`
separe primero los ítems generales y luego agrupe por ciclo y curso. Usar
`dict(Curso.DIVISIONES)` para títulos y este mapa para abreviaturas:

```python
ETIQUETAS_CORTAS_CICLO = {
    "CB": "C.B.",
    "CS": "C.S.",
}
```

El título de curso se construye como
`f"{_anio_ordinal(curso)} {etiqueta_corta}"`, donde `_anio_ordinal("1ro")`
devuelve `"1.º"`, `_anio_ordinal("2do")` devuelve `"2.º"` y conserva un valor
desconocido sin transformarlo. Los ítems sin curso dentro de un ciclo forman
el grupo `Para todo el ciclo` antes de los cursos.

- [ ] **Step 4: Ejecutar selector y vista afectada**

Run: `pytest contenidos/tests/test_selectors.py web/tests/test_views.py::test_categoria_detalle_muestra_sus_productos_activos -q`

Expected: selector PASS; la vista puede fallar hasta adaptar su expectativa de contexto al nuevo diccionario. Actualizar esa expectativa a
`response.context["bloques_productos"]["generales"]["grupos_precio"][0]` y repetir hasta obtener PASS.

- [ ] **Step 5: Registrar el avance**

```bash
git add contenidos/selectors.py contenidos/tests/test_selectors.py web/tests/test_views.py
git commit -m "Agrupar catálogo por ciclos y cursos"
```

### Task 2: Layout vertical y tablas reutilizables

**Files:**
- Create: `templates/components/product_price_tables.html`
- Modify: `templates/web/categoria_detalle.html`
- Modify: `static/css/uni2-design-system.css`
- Modify: `web/tests/test_views.py`
- Modify: `especificacion/pantallas/sitio-publico.md`
- Modify: `especificacion/reglas/productos-servicios.md`

**Interfaces:**
- Consumes: diccionario jerárquico de Task 1.
- Produces: partial `components/product_price_tables.html`, que recibe `grupos_precio` y `tabla_label`.
- Produces: clases `uni2-category-detail-layout`, `uni2-category-products-panel`, `uni2-cycle-section`, `uni2-cycle-heading` y `uni2-course-group`.

- [ ] **Step 1: Escribir pruebas fallidas del orden visual y los grupos**

En `web/tests/test_views.py`, ampliar el caso de categoría con ambos ciclos y
comprobar:

```python
assert 'class="uni2-category-detail-layout"' in contenido
assert 'class="uni2-detail-layout"' not in contenido
assert contenido.index('id="categoria-title"') < contenido.index('class="uni2-category-products-panel"')
assert "Ciclo Básico" in contenido
assert "Ciclo Superior" in contenido
assert "1.º C.B." in contenido
assert "1.º C.S." in contenido
```

Conservar las aserciones existentes para `data-price-type`, enlaces únicos,
fotos, encabezados deducidos, ausencia de `Disponibilidad` y columnas de
precio. Agregar una prueba independiente que compruebe que la ficha individual
sí mantiene `class="uni2-detail-layout"`.

- [ ] **Step 2: Ejecutar las pruebas de vista y comprobar el fallo**

Run: `pytest web/tests/test_views.py -q`

Expected: FAIL porque la categoría todavía usa el grid horizontal y títulos planos.

- [ ] **Step 3: Extraer el partial de tablas**

Mover al partial el bucle completo de `grupos_precio`, incluidos encabezados,
filas, miniaturas, enlaces y cuatro escenarios. Construir el `aria-label` con
`tabla_label` y el nombre del escenario. El grupo `sin_precio` debe seguir
renderizando solamente la columna de nombre.

- [ ] **Step 4: Reorganizar la plantilla de categoría**

Reemplazar `uni2-detail-layout` por `uni2-category-detail-layout`. Renderizar
el encabezado primero y luego `uni2-category-products-panel` a todo el ancho.
Dentro del panel:

1. incluir el partial para `bloques_productos.generales`, si existe;
2. recorrer `bloques_productos.ciclos`;
3. crear una sección por ciclo con su encabezado;
4. recorrer sus grupos y usar el título `Para todo el ciclo` o `1.º C.B.`;
5. incluir el partial para cada lista `grupos_precio`;
6. mantener después la imagen informativa y el contacto.

No conservar el título genérico `Precios`: el título de categoría, los ciclos y
los cursos ya aportan la jerarquía necesaria.

- [ ] **Step 5: Agregar estilos acotados y documentar la pantalla**

Definir el flujo vertical, separación, panel a todo el ancho, encabezado de
ciclo y subtítulos de curso solo bajo las nuevas clases. En
`sitio-publico.md`, reemplazar “introducción a la izquierda y panel a la
derecha” por la jerarquía vertical. En la regla pública, documentar ciclo como
nivel principal y curso como segundo nivel.

- [ ] **Step 6: Ejecutar pruebas de selector y vistas**

Run: `pytest contenidos/tests/test_selectors.py web/tests/test_views.py -q`

Expected: PASS.

- [ ] **Step 7: Registrar el avance**

```bash
git add templates/components/product_price_tables.html templates/web/categoria_detalle.html static/css/uni2-design-system.css web/tests/test_views.py especificacion/pantallas/sitio-publico.md especificacion/reglas/productos-servicios.md
git commit -m "Ordenar categorías en un layout vertical"
```

### Task 3: Selector accesible de ciclos en mobile

**Files:**
- Create: `static/js/uni2-cycle-selector.js`
- Modify: `templates/web/categoria_detalle.html`
- Modify: `static/css/uni2-design-system.css`
- Modify: `web/tests/test_views.py`
- Modify: `especificacion/arquitectura/design-system-conceptos.md`
- Modify: `especificacion/pantallas/sitio-publico.md`

**Interfaces:**
- Consumes: `bloques_productos.mostrar_selector_ciclos` y cada `ciclo.slug`.
- Produces: markup `data-cycle-selector`, `data-cycle-tabs`, `data-cycle-tab` y `data-cycle-panel`.
- Produce: comportamiento progresivo inicializado al cargar el documento.

- [ ] **Step 1: Escribir pruebas fallidas del contrato HTML**

Crear una categoría con CB y CS y comprobar:

```python
assert 'data-cycle-selector' in contenido
assert 'role="tablist"' in contenido
assert 'data-cycle-tab="cb"' in contenido
assert 'aria-controls="uni2-cycle-panel-cb"' in contenido
assert 'data-cycle-tab="cs"' in contenido
assert 'aria-controls="uni2-cycle-panel-cs"' in contenido
assert 'id="uni2-cycle-panel-cb"' in contenido
assert 'id="uni2-cycle-panel-cs"' in contenido
assert 'src="/static/js/uni2-cycle-selector.js"' in contenido
```

En una categoría con solo CB, comprobar que no existe `role="tablist"`, pero
sí el panel y su contenido.

- [ ] **Step 2: Ejecutar las pruebas y comprobar el fallo**

Run: `pytest web/tests/test_views.py -q`

Expected: FAIL por ausencia del contrato de pestañas y del script.

- [ ] **Step 3: Agregar markup progresivo**

Renderizar el tablist con atributo HTML `hidden`, un botón por ciclo y
`aria-selected="false"`. Cada sección de ciclo se renderiza visible y recibe
`data-cycle-panel` e identificador estable. Cargar el script desde el bloque
`extra_scripts` de la plantilla.

- [ ] **Step 4: Implementar el controlador mobile**

En `uni2-cycle-selector.js`, usar una IIFE, `querySelectorAll` y
`window.matchMedia("(max-width: 575.98px)")`. En mobile, quitar `hidden` del
tablist, seleccionar CB cuando existe o el primer ciclo disponible y ocultar
los demás paneles con `hidden`. En desktop, ocultar el tablist y quitar
`hidden` de todos los paneles. Cada click debe actualizar `aria-selected`,
`tabindex` y paneles; las flechas izquierda/derecha deben mover selección y
foco entre botones. Escuchar el evento `change` del media query.

- [ ] **Step 5: Estilizar y documentar el selector**

Agregar estilos para el control segmentado solamente bajo
`@media (max-width: 575.98px)`. Documentar sus clases y el comportamiento
progresivo en los dos archivos OKF indicados.

Cada ciclo debe ser una card independiente: C.B. con acento azul y C.S. con
acento verde. Las dos cards se ubican lado a lado desde desktop ancho, se apilan
en anchos intermedios y el selector deja una sola visible en mobile. El bloque
general usa una card neutral separada y de ancho completo.

- [ ] **Step 6: Verificar lógica, accesibilidad y responsive**

Run: `pytest web/tests/test_views.py contenidos/tests/test_selectors.py -q`

Expected: PASS.

Levantar Django y capturar `/servicios/<pk>/` en `1280x1000` y `390x844` con
Chromium. Confirmar visualmente que desktop muestra ambos ciclos, mobile uno
solo, el tab seleccionado coincide con el panel y el encabezado está por
encima del listado.

- [ ] **Step 7: Registrar el avance**

```bash
git add static/js/uni2-cycle-selector.js templates/web/categoria_detalle.html static/css/uni2-design-system.css web/tests/test_views.py especificacion/arquitectura/design-system-conceptos.md especificacion/pantallas/sitio-publico.md
git commit -m "Agregar selector mobile de ciclos"
```

### Task 4: Verificación integral y cierre documental

**Files:**
- Review: `especificacion/casos-de-uso/cu-listar-productos-servicios-publicos.md`
- Review: `docs/superpowers/specs/2026-08-14-layout-vertical-categoria-productos-design.md`
- Review: todos los archivos modificados en Tasks 1–3.

**Interfaces:**
- Consumes: catálogo jerárquico, layout vertical y selector mobile terminados.
- Produces: implementación verificada y documentación sin contradicciones.

- [ ] **Step 1: Alinear el caso de uso**

Actualizar el flujo público para indicar que la categoría muestra primero los
ciclos, luego sus cursos, y que en mobile se selecciona un ciclo por vez cuando
existen ambos.

- [ ] **Step 2: Revisar consistencia y formato**

Run: `git diff --check`

Run: `python3 manage.py check`

Run: `python3 manage.py makemigrations --check`

Expected: todos terminan con código 0 y sin advertencias nuevas.

- [ ] **Step 3: Ejecutar la suite completa**

Run: `pytest -q`

Expected: toda la suite pasa sin fallos.

- [ ] **Step 4: Revisar el diff final**

Confirmar que no se modificaron modelos ni se generaron migraciones por este
cambio; distinguir los cambios relacionados ya existentes de cualquier cambio
ajeno antes de preparar un commit.

- [ ] **Step 5: Registrar la documentación final si quedó fuera de commits anteriores**

```bash
git add especificacion/casos-de-uso/cu-listar-productos-servicios-publicos.md
git commit -m "Documentar navegación por ciclos de productos"
```
