# Alineación del rediseño con el design system Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Conservar las mejoras funcionales y de jerarquía visual del PR #42 usando el design system Uni2, con extensiones compartidas mínimas y sin las familias paralelas `uni2-ops-*`, `uni2-member-*` y `uni2-access-*`.

**Architecture:** La migración se hace desde la base hacia las pantallas: primero se amplía y documenta el contrato de los componentes genéricos; luego se migran home, experiencia del asociado y gestión en commits independientes; por último se eliminan los estilos huérfanos y se verifican las ocho pantallas contra la línea base. No cambian modelos, permisos, URLs ni reglas de negocio.

**Tech Stack:** Django Templates, Bootstrap 5, CSS custom properties, pytest, pytest-django, SQLite para verificación local y Chromium headless para revisión visual.

## Global Constraints

- La fuente funcional es el bundle OKF iniciado en `especificacion/index.md`; toda decisión relevante se actualiza en el archivo más específico durante el mismo cambio.
- Usar Bootstrap 5 y Templates Django; no agregar React, otra hoja de estilos ni dependencias frontend.
- Reutilizar primero; extender solo `uni2-metric-card`, `uni2-badge` y `uni2-surface-card`, y crear únicamente `uni2-avatar` y `uni2-data-list`.
- Los modificadores semánticos admitidos son `info`, `success`, `warning` y `danger`; los avatares admiten azul, verde, amarillo y rojo.
- No crear otra escala tipográfica: usar `uni2-titulo-principal`, `uni2-titulo-seccion`, `uni2-titulo-componente` y `uni2-section-kicker`.
- Usar tokens `--color-*`, `--radius-*`, `--shadow-*`, `--font-*`, `--line-height-*` y `--motion-*`; no introducir literales repetidos para esas decisiones.
- Los únicos cortes responsive nuevos permitidos son los de Bootstrap: `991.98px`, `767.98px` y `575.98px`.
- Credencial y cuotas usan `container py-5` y encabezado simple; no usan hero propio.
- Los errores generales usan `components/alert.html`; cada error concreto permanece junto a su campo.
- Se pueden conservar clases `uni2-cobro-*` y `uni2-period-*` solo cuando expresen estructura exclusiva de esos flujos.
- No modificar modelos ni generar migraciones.
- El CSS final puede agregar como máximo 500 líneas respecto de `origin/staging`.
- Las capturas de comparación son locales y no se agregan al repositorio.
- Los commits se escriben en castellano.

---

## Mapa de archivos y responsabilidades

- `static/css/uni2-design-system.css`: única implementación de tokens y componentes visuales compartidos.
- `templates/web/design-system.html`: catálogo ejecutable y ejemplos reales de cada componente público.
- `web/tests/test_views.py`: contrato estructural del catálogo, tokens, breakpoints y familias de clases permitidas.
- `templates/components/service_card.html`: componente existente para servicios y accesos adicionales de la home.
- `templates/components/alert.html`: componente existente para resúmenes y mensajes de formulario.
- `templates/web/home.html`: composición de la home; no define componentes nuevos.
- `templates/asociados/credencial.html`: credencial, QR, consentimiento y disponibilidad offline.
- `templates/asociados/cuotas.html`: resumen y tabla de cuotas del asociado.
- `asociados/views.py`: mantiene los datos agregados `cuotas_total` y `cuotas_con_saldo`; no recibe lógica visual nueva.
- `asociados/tests/test_views.py`: comportamiento y estructura visible de credencial y cuotas.
- `templates/gestion/asociados.html`: búsqueda, filtros, acciones y resultados de asociados.
- `templates/gestion/deudores.html`: consulta de deuda y acceso contextual al asociado.
- `templates/gestion/periodos_cuota.html`: alta, listado y generación de períodos.
- `templates/gestion/asociado_form.html`: formulario de alta compartido.
- `templates/gestion/asociado_editar.html`: formulario de edición y baja.
- `templates/gestion/asociado_detalle.html`: ficha operativa y sus acciones.
- `templates/gestion/cobrar_cuotas.html`: selección de cuotas, importe, método y donación.
- `templates/gestion/asociado_cuotas.html`: navegación histórica conservada.
- `gestion/tests/test_views.py`: comportamiento, permisos, acciones, errores y marcado estructural de gestión.
- `especificacion/arquitectura/design-system.md`: responsabilidad, límites y reglas de composición de los componentes.
- `especificacion/arquitectura/design-system-conceptos.md`: inventario de clases públicas.
- `especificacion/pantallas/sitio-publico.md`: composición de los accesos adicionales de la home.
- `especificacion/pantallas/asociado.md`: estructura aprobada para credencial y cuotas.
- `especificacion/pantallas/gestion.md`: composición visual de las pantallas operativas sin un subsistema paralelo.

---

### Task 1: Ampliar el contrato compartido del design system

**Files:**
- Modify: `web/tests/test_views.py`
- Modify: `static/css/uni2-design-system.css`
- Modify: `templates/web/design-system.html`
- Modify: `especificacion/arquitectura/design-system.md`
- Modify: `especificacion/arquitectura/design-system-conceptos.md`

**Interfaces:**
- Consumes: tokens y componentes `uni2-metric-card`, `uni2-badge` y `uni2-surface-card` existentes.
- Produces: `uni2-metric-card-{info|success|warning|danger}`, `uni2-badge-{info|success|warning|danger}`, `uni2-surface-card-{info|success|warning|danger}`, `uni2-avatar`, `uni2-avatar-{blue|green|yellow|red}` y `uni2-data-list`.

- [ ] **Step 1: Escribir el test de catálogo que fija el contrato público**

Agregar dentro de `test_design_system_porta_secciones_del_showcase`:

```python
    for clase in (
        "uni2-metric-card-info",
        "uni2-metric-card-success",
        "uni2-metric-card-warning",
        "uni2-metric-card-danger",
        "uni2-badge-info",
        "uni2-badge-success",
        "uni2-badge-warning",
        "uni2-badge-danger",
        "uni2-surface-card-info",
        "uni2-surface-card-success",
        "uni2-surface-card-warning",
        "uni2-surface-card-danger",
        "uni2-avatar",
        "uni2-data-list",
    ):
        assert clase in content
    assert "No representa un dashboard" not in content
```

- [ ] **Step 2: Ejecutar el test y comprobar el fallo esperado**

Run: `DB_ENGINE=sqlite uv run pytest web/tests/test_views.py::test_design_system_porta_secciones_del_showcase -q`

Expected: FAIL porque el catálogo todavía no muestra los modificadores, avatar y lista de datos.

- [ ] **Step 3: Agregar al CSS las extensiones mínimas con tokens existentes**

Mantener la raíz existente de cada componente y agregar modificadores semánticos. La estructura a implementar es:

```css
.uni2-metric-card,
.uni2-surface-card { border-top: 0.35rem solid var(--uni2-component-accent, var(--brand-blue)); }
.uni2-metric-card-info,
.uni2-surface-card-info { --uni2-component-accent: var(--brand-blue); }
.uni2-metric-card-success,
.uni2-surface-card-success { --uni2-component-accent: var(--brand-green); }
.uni2-metric-card-warning,
.uni2-surface-card-warning { --uni2-component-accent: var(--brand-yellow); }
.uni2-metric-card-danger,
.uni2-surface-card-danger { --uni2-component-accent: var(--brand-red); }

.uni2-badge-info { background: color-mix(in srgb, var(--brand-blue) 14%, transparent); color: var(--color-action-on-surface); }
.uni2-badge-success { background: color-mix(in srgb, var(--brand-green) 14%, transparent); color: var(--color-success-text); }
.uni2-badge-warning { background: color-mix(in srgb, var(--brand-yellow) 18%, transparent); color: var(--color-warning-text); }
.uni2-badge-danger { background: color-mix(in srgb, var(--brand-red) 12%, transparent); color: var(--color-danger-text); }

.uni2-avatar {
  display: inline-grid;
  width: 2.5rem;
  height: 2.5rem;
  flex: 0 0 2.5rem;
  place-items: center;
  border-radius: 50%;
  font-weight: 700;
}
.uni2-avatar-blue { background: var(--brand-blue); color: var(--color-on-strong); }
.uni2-avatar-green { background: var(--brand-green); color: var(--color-on-bright); }
.uni2-avatar-yellow { background: var(--brand-yellow); color: var(--color-on-bright); }
.uni2-avatar-red { background: var(--brand-red-dark); color: var(--color-on-strong); }

.uni2-data-list { margin: 0; }
.uni2-data-list > div {
  display: grid;
  grid-template-columns: minmax(8rem, 0.8fr) minmax(0, 1.2fr);
  gap: 1rem;
  padding-block: 0.75rem;
  border-bottom: 1px solid var(--color-border);
}
.uni2-data-list > div:last-child { border-bottom: 0; }
.uni2-data-list dt { color: var(--color-text-muted); font-weight: 600; }
.uni2-data-list dd { margin: 0; overflow-wrap: anywhere; }
```

Antes de guardar, confirmar que todos los tokens usados ya existen con:

Run: `rg -n -- '--(brand-(blue|green|yellow|red)|color-(action-on-surface|success-text|warning-text|danger-text|on-strong|on-bright|border|text-muted)):' static/css/uni2-design-system.css`

Expected: todos los tokens del bloque aparecen definidos en `:root`; no crear tokens adicionales para duplicarlos.

- [ ] **Step 4: Agregar ejemplos completos al catálogo**

En `templates/web/design-system.html`, reemplazar el texto que restringe métricas a importaciones y mostrar las cuatro variantes. Agregar, en la misma sección de componentes, este tipo de muestras:

```html
<span class="uni2-badge uni2-badge-info">Con usuario</span>
<span class="uni2-badge uni2-badge-success">Al día</span>
<span class="uni2-badge uni2-badge-warning">Pendiente</span>
<span class="uni2-badge uni2-badge-danger">Con deuda</span>

<span class="uni2-avatar uni2-avatar-blue" aria-hidden="true">ML</span>

<dl class="uni2-data-list">
    <div><dt>Número</dt><dd>1024</dd></div>
    <div><dt>Estado</dt><dd>Activo</dd></div>
</dl>
```

Las surface cards y métricas deben mostrar las cuatro variantes y su nombre de clase en `<code>`.

- [ ] **Step 5: Documentar responsabilidad, límites e inventario**

En `especificacion/arquitectura/design-system.md`, agregar que:

- las métricas resumen un dato operativo real y no reemplazan tablas ni títulos;
- los badges expresan estado con texto y no dependen solo del color;
- los acentos de surface cards agrupan una unidad sin permitir cards anidadas;
- el avatar muestra iniciales o imagen y no es un control interactivo;
- la data list representa pares etiqueta/valor y no reemplaza tablas comparativas.

En `especificacion/arquitectura/design-system-conceptos.md`, incorporar todas las clases producidas en **Interfaces**, con una fila por raíz y por familia de modificadores.

- [ ] **Step 6: Ejecutar los tests estructurales del design system**

Run: `DB_ENGINE=sqlite uv run pytest web/tests/test_views.py -k 'design_system or catalogo or css' -q`

Expected: PASS.

- [ ] **Step 7: Confirmar que el diff solo amplía componentes compartidos y hacer commit**

Run: `git diff --check`

```bash
git add web/tests/test_views.py static/css/uni2-design-system.css templates/web/design-system.html especificacion/arquitectura/design-system.md especificacion/arquitectura/design-system-conceptos.md
git commit -m "Ampliar componentes operativos del design system"
```

### Task 2: Reutilizar service cards en los accesos adicionales de la home

**Files:**
- Modify: `gestion/tests/test_views.py`
- Modify: `templates/web/home.html`
- Modify: `static/css/uni2-design-system.css`
- Modify: `especificacion/pantallas/sitio-publico.md`

**Interfaces:**
- Consumes: `templates/components/service_card.html`, con `url`, `color`, `icono`, `titulo`, `descripcion` y `texto_enlace`.
- Produces: la sección `Más accesos` compuesta con grilla Bootstrap y `uni2-service-card`, sin clases `uni2-access-*`.

- [ ] **Step 1: Fijar la composición esperada de la home administrativa**

Extender `test_home_gestion_muestra_accesos_basicos`:

```python
    assert "uni2-service-card" in content
    assert "uni2-access-" not in content
```

- [ ] **Step 2: Ejecutar el test y comprobar que falla por las clases actuales**

Run: `DB_ENGINE=sqlite uv run pytest gestion/tests/test_views.py::test_home_gestion_muestra_accesos_basicos -q`

Expected: FAIL en `assert "uni2-access-" not in content`.

- [ ] **Step 3: Reemplazar el lanzador por el componente compartido**

En `templates/web/home.html`, conservar título, datos y destinos; reemplazar el bloque `uni2-access-*` por:

```django
<section class="mb-5" aria-labelledby="otros-accesos-title">
    <div class="uni2-section-heading">
        <div>
            <h2 id="otros-accesos-title" class="uni2-titulo-componente">Más accesos</h2>
            <p>Acciones disponibles para tu perfil.</p>
        </div>
    </div>
    <div class="row g-3">
        {% for action in home_navigation.extra_actions %}
            <div class="col-12 col-md-6 col-lg-4">
                {% cycle 'uni2-service-card-blue' 'uni2-service-card-green' 'uni2-service-card-yellow' 'uni2-service-card-red' as card_color silent %}
                {% include "components/service_card.html" with url=action.url color=card_color icono="arrow-up-right-circle" titulo=action.label descripcion=action.description texto_enlace="Ir" %}
            </div>
        {% endfor %}
    </div>
</section>
```

Confirmar que esos cuatro modificadores compartidos existen:

Run: `rg -n 'uni2-service-card-(blue|green|yellow|red)' static/css/uni2-design-system.css templates/web/design-system.html`

Expected: los cuatro modificadores están implementados en el CSS; no agregar modificadores nuevos.

- [ ] **Step 4: Eliminar todo el bloque CSS `uni2-access-*` y sus reglas responsive**

Run: `rg -n 'uni2-access-' static/css/uni2-design-system.css templates`

Expected después de editar: sin coincidencias.

- [ ] **Step 5: Actualizar la pantalla pública en la especificación**

En `especificacion/pantallas/sitio-publico.md`, declarar que `Más accesos` usa una grilla Bootstrap de `uni2-service-card`, con las mismas reglas de permisos y prioridad existentes.

- [ ] **Step 6: Verificar home pública y administrativa**

Run: `DB_ENGINE=sqlite uv run pytest web/tests/test_views.py gestion/tests/test_views.py -k 'home' -q`

Expected: PASS.

- [ ] **Step 7: Hacer commit**

```bash
git add gestion/tests/test_views.py templates/web/home.html static/css/uni2-design-system.css especificacion/pantallas/sitio-publico.md
git commit -m "Reutilizar tarjetas compartidas en los accesos"
```

### Task 3: Alinear credencial y cuotas del asociado

**Files:**
- Modify: `asociados/tests/test_views.py`
- Modify: `templates/asociados/credencial.html`
- Modify: `templates/asociados/cuotas.html`
- Modify: `static/css/uni2-design-system.css`
- Modify: `especificacion/pantallas/asociado.md`

**Interfaces:**
- Consumes: métricas, badges y surface cards de Task 1; `uni2-credential` existente; datos `cuotas_total` y `cuotas_con_saldo` de `asociados/views.py`.
- Produces: dos pantallas con `container py-5`, encabezado simple y sin clases `uni2-member-*` ni `uni2-ops-*`.

- [ ] **Step 1: Agregar tests estructurales de credencial y cuotas**

Agregar al final de `asociados/tests/test_views.py`:

```python
@pytest.mark.django_db
@pytest.mark.parametrize("url_name", ["asociados:credencial", "asociados:cuotas"])
def test_pantallas_asociado_usan_contenedor_sin_familias_paralelas(client, url_name):
    asociado = create_asociado(
        nombre="Nora",
        apellido="Diseño",
        dni="40999111",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 8, 1),
    )
    client.force_login(asociado.usuario)

    content = client.get(reverse(url_name)).content.decode()

    assert 'class="container py-5' in content
    assert "uni2-member-" not in content
    assert "uni2-ops-" not in content


@pytest.mark.django_db
def test_cuotas_asociado_usan_metricas_y_superficie_compartidas(client):
    asociado = create_asociado(
        nombre="Leo",
        apellido="Cuotas",
        dni="40999222",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 8, 1),
    )
    client.force_login(asociado.usuario)

    content = client.get(reverse("asociados:cuotas")).content.decode()

    assert "uni2-metric-card" in content
    assert "uni2-surface-card" in content
```

- [ ] **Step 2: Ejecutar solamente los tests de ambas pantallas**

Run: `DB_ENGINE=sqlite uv run pytest asociados/tests/test_views.py -k 'credencial or cuotas' -q`

Expected: FAIL por presencia de `uni2-member-*` y `uni2-ops-*`.

- [ ] **Step 3: Migrar la credencial sin alterar su comportamiento**

En `templates/asociados/credencial.html`:

- usar un encabezado simple con `uni2-section-kicker` y `uni2-titulo-principal`;
- conservar `uni2-credential`, QR, estado, token, consentimiento, acciones y textos offline;
- reemplazar layout `uni2-member-offline-copy` por `d-flex flex-column flex-md-row gap-3 align-items-md-center`;
- eliminar la marca decorativa duplicada `uni2-member-card-mark`.

No cambiar nombres de campos, URLs, bloques condicionales ni atributos accesibles del QR.

- [ ] **Step 4: Migrar cuotas a métricas y tablas compartidas**

En `templates/asociados/cuotas.html`, usar una grilla:

```django
<div class="row g-3 mb-4" aria-label="Resumen de cuotas">
    <div class="col-12 col-sm-4">
        <div class="card uni2-metric-card {% if total_deuda > 0 %}uni2-metric-card-danger{% else %}uni2-metric-card-success{% endif %}">
            <div class="card-body">
                <div class="uni2-metric-label">Deuda total</div>
                <div class="uni2-metric-value">{{ total_deuda|moneda }}</div>
            </div>
        </div>
    </div>
</div>
```

Completar la misma grilla con los dos indicadores que ya muestra el template, sin inventar métricas. Usar `card uni2-surface-card uni2-surface-card-info`, `table-responsive`, `table table-soft` y badges semánticos para estado/saldo.

- [ ] **Step 5: Eliminar las reglas `uni2-member-*` del CSS**

Run: `rg -n 'uni2-member-' templates static/css/uni2-design-system.css`

Expected después de editar: sin coincidencias.

- [ ] **Step 6: Documentar la composición concreta del asociado**

En `especificacion/pantallas/asociado.md`, mantener todas las reglas funcionales y agregar que credencial usa el componente existente sin hero, mientras cuotas usa métricas semánticas y una surface card sin alterar el resumen ni la tabla.

- [ ] **Step 7: Ejecutar tests y hacer commit**

Run: `DB_ENGINE=sqlite uv run pytest asociados/tests/test_views.py -q`

Expected: PASS.

```bash
git add asociados/tests/test_views.py templates/asociados/credencial.html templates/asociados/cuotas.html static/css/uni2-design-system.css especificacion/pantallas/asociado.md
git commit -m "Alinear pantallas del asociado con el design system"
```

### Task 4: Migrar listados y períodos de gestión

**Files:**
- Modify: `gestion/tests/test_views.py`
- Modify: `templates/gestion/asociados.html`
- Modify: `templates/gestion/deudores.html`
- Modify: `templates/gestion/periodos_cuota.html`
- Modify: `especificacion/pantallas/gestion.md`

**Interfaces:**
- Consumes: `uni2-avatar`, métricas, badges y surface cards de Task 1; `components/alert.html`.
- Produces: búsqueda de asociados, deudores y períodos sin clases `uni2-ops-*`, manteniendo filtros, formularios, permisos, filas y destinos.

- [ ] **Step 1: Crear un helper de aserción estructural para gestión**

Agregar cerca de `crear_usuario_gestion` en `gestion/tests/test_views.py`:

```python
def assert_usa_design_system_compartido(content):
    assert "uni2-surface-card" in content
    assert "uni2-ops-" not in content
```

Invocarlo sobre la variable `content` de estos tests concretos:

- `test_asociados_gestion_busca_y_muestra_detalle`; agregar también `assert "uni2-avatar" in content`;
- `test_deudores_gestion_lista_asociados_y_linkea_a_cobro`;
- `test_periodos_cuota_gestion_muestra_alerta_de_errores`; agregar también `assert "uni2-alert-danger" in content`.

- [ ] **Step 2: Ejecutar los tests focalizados y comprobar los fallos**

Run: `DB_ENGINE=sqlite uv run pytest gestion/tests/test_views.py -k 'asociados or deudores or periodos_cuota' -q`

Expected: FAIL por las clases `uni2-ops-*` y el resumen de error propio.

- [ ] **Step 3: Migrar encabezados, filtros y resultados de asociados/deudores**

En ambos templates:

- quitar `uni2-ops-page`, `uni2-ops-shell` y hero operativo;
- usar breadcrumb existente, encabezado con `d-flex flex-column flex-lg-row gap-3 justify-content-between` y `uni2-page-header-actions`;
- usar `card uni2-surface-card uni2-surface-card-{variant}` para filtros/resultados;
- usar grilla Bootstrap con `uni2-metric-card` solo para datos que el template ya recibe;
- reemplazar avatares por `uni2-avatar uni2-avatar-{color}`;
- reemplazar estados por `uni2-badge uni2-badge-{variant}`;
- conservar `table-responsive`, `table-soft`, enlace único por fila, queries y botones autorizados.

- [ ] **Step 4: Migrar períodos y su formulario**

En `templates/gestion/periodos_cuota.html`:

- aplicar el mismo encabezado simple y surface cards;
- reemplazar el resumen `uni2-form-error-summary` por:

```django
{% if form.errors %}
    {% include "components/alert.html" with variant="danger" title="Revisá los datos ingresados" message="Hay campos con errores. Corregilos para continuar." %}
{% endif %}
```

- conservar `{{ field.errors }}` junto a cada campo;
- conservar `uni2-period-amounts`, `uni2-period-generate-action` y `uni2-period-generate-count` porque expresan estructura del dominio;
- reemplazar los estados por badges semánticos.

- [ ] **Step 5: Actualizar la especificación de gestión**

En `especificacion/pantallas/gestion.md`, reemplazar la descripción de una “capa visual operativa” propia por la composición concreta: encabezados, acciones, métricas, surface cards, avatares, badges, tablas y alertas del design system compartido. Mantener intactas las decisiones funcionales y de permisos.

- [ ] **Step 6: Ejecutar tests focalizados y hacer commit**

Run: `DB_ENGINE=sqlite uv run pytest gestion/tests/test_views.py -k 'asociados or deudores or periodos_cuota' -q`

Expected: PASS.

```bash
git add gestion/tests/test_views.py templates/gestion/asociados.html templates/gestion/deudores.html templates/gestion/periodos_cuota.html especificacion/pantallas/gestion.md
git commit -m "Reutilizar componentes compartidos en listados de gestión"
```

### Task 5: Migrar ficha, formularios y cobro de gestión

**Files:**
- Modify: `gestion/tests/test_views.py`
- Modify: `templates/gestion/asociado_form.html`
- Modify: `templates/gestion/asociado_editar.html`
- Modify: `templates/gestion/asociado_detalle.html`
- Modify: `templates/gestion/cobrar_cuotas.html`
- Modify: `templates/gestion/asociado_cuotas.html`
- Modify: `static/css/uni2-design-system.css`
- Modify: `especificacion/pantallas/gestion.md`

**Interfaces:**
- Consumes: componentes de Task 1, alert compartida, reglas de navegación/permiso existentes y clases estructurales `uni2-cobro-*`.
- Produces: ficha, alta, edición, historial y cobro sin clases visuales paralelas, con `uni2-data-list` para pares etiqueta/valor.

- [ ] **Step 1: Extender los tests GET y de validación existentes**

Agregar las aserciones estructurales a estos tests concretos: `test_asociado_detalle_muestra_a_que_corresponde_pago_reciente`, `test_asociado_editar_muestra_formulario_separado`, `test_asociado_nuevo_crea_asociado_desde_gestion` y `test_cobros_renderiza_saldo_y_etiqueta_accesible_para_cada_cuota`. Usar, según el contenido de cada pantalla:

```python
assert "uni2-ops-" not in content
assert "uni2-data-list" in content
```

En respuestas de formularios inválidos agregar:

```python
assert "uni2-alert-danger" in content
assert "uni2-form-error-summary" not in content
```

En el test de cobro que renderiza cuotas, conservar la aserción existente del período en el nombre accesible del checkbox y agregar `assert "uni2-cobro-check" in content`.

- [ ] **Step 2: Ejecutar el grupo de tests y comprobar los fallos estructurales**

Run: `DB_ENGINE=sqlite uv run pytest gestion/tests/test_views.py -k 'asociado_detalle or asociado_form or asociado_editar or cobrar_cuotas' -q`

Expected: FAIL por clases `uni2-ops-*`, `uni2-record-list` o resumen propio.

- [ ] **Step 3: Migrar alta y edición**

En `asociado_form.html` y `asociado_editar.html`:

- usar encabezado simple y `uni2-page-header-actions`;
- mantener orden, nombres, `help_text`, valores, POST, CSRF y botones;
- usar una sola `card uni2-surface-card uni2-surface-card-info` por formulario;
- renderizar el alert compartido una vez cuando `form.errors` sea verdadero;
- mantener cada `field.errors` inmediatamente después del widget;
- reemplazar contenedores de acciones por utilidades `d-flex flex-column flex-sm-row gap-2`.

- [ ] **Step 4: Migrar el detalle y su información**

En `asociado_detalle.html`:

- sustituir hero por encabezado simple con avatar, identidad y `uni2-page-header-actions`;
- representar deuda/estado con métricas y badges semánticos;
- reemplazar `uni2-record-list` por `uni2-data-list` sin cambiar etiquetas ni valores;
- conservar `volver`, `Cobrar`, `Editar asociado`, cuotas, pagos, auditoría y sus condicionales de permiso;
- no introducir cards anidadas: cada panel temático es una surface card y sus listas/tablas quedan directamente dentro.

- [ ] **Step 5: Migrar cobro e historial sin tocar reglas de negocio**

En `cobrar_cuotas.html` y `asociado_cuotas.html`:

- reemplazar encabezados/paneles genéricos por componentes compartidos;
- conservar `uni2-cobro-summary`, `uni2-cobro-section`, `uni2-cobro-check`, `uni2-cobro-fields` y `uni2-cobro-field-full`;
- eliminar clases `uni2-ops-side-card*` y expresar esos bloques con `uni2-surface-card-{warning|success}`;
- conservar orden de cuotas, inputs, cálculo mostrado, donación, POST, CSRF, cancelación y etiqueta accesible por período.

- [ ] **Step 6: Eliminar CSS específico que ya fue reemplazado**

Eliminar reglas de:

```text
uni2-form-error-summary
uni2-associate-record-hero
uni2-associate-record-heading
uni2-associate-record-avatar
uni2-record-list
uni2-ops-side-card
```

Run: `rg -n 'uni2-(form-error-summary|associate-record|record-list|ops-side-card)' templates static/css/uni2-design-system.css`

Expected: sin coincidencias.

- [ ] **Step 7: Completar la especificación y ejecutar tests**

En `especificacion/pantallas/gestion.md`, documentar que la ficha usa avatar, métricas, data lists y surface cards compartidas, y que cobro conserva clases específicas solo para selección/resumen.

Run: `DB_ENGINE=sqlite uv run pytest gestion/tests/test_views.py -q`

Expected: PASS.

- [ ] **Step 8: Hacer commit**

```bash
git add gestion/tests/test_views.py templates/gestion/asociado_form.html templates/gestion/asociado_editar.html templates/gestion/asociado_detalle.html templates/gestion/cobrar_cuotas.html templates/gestion/asociado_cuotas.html static/css/uni2-design-system.css especificacion/pantallas/gestion.md
git commit -m "Alinear ficha y cobros con el design system"
```

### Task 6: Eliminar la familia operativa paralela y agregar guardrails

**Files:**
- Modify: `web/tests/test_views.py`
- Modify: `static/css/uni2-design-system.css`
- Modify: any productive template still reported by the scans below
- Modify: `especificacion/arquitectura/design-system-conceptos.md`

**Interfaces:**
- Consumes: todas las pantallas migradas en Tasks 2–5.
- Produces: un único vocabulario visual compartido y un test que impide reintroducir las familias reemplazadas.

- [ ] **Step 1: Escribir el test de familias prohibidas**

Agregar a `web/tests/test_views.py`:

```python
def test_redisenio_no_conserva_familias_visuales_paralelas():
    project_root = Path(__file__).resolve().parents[2]
    archivos = [project_root / "static/css/uni2-design-system.css"]
    archivos.extend((project_root / "templates").rglob("*.html"))
    contenido = "\n".join(path.read_text(encoding="utf-8") for path in archivos)

    for familia in (
        "uni2-ops-",
        "uni2-member-",
        "uni2-access-",
        "uni2-form-error-summary",
        "uni2-record-list",
    ):
        assert familia not in contenido
```

- [ ] **Step 2: Ejecutar el test y usar el fallo como lista de migraciones pendientes**

Run: `DB_ENGINE=sqlite uv run pytest web/tests/test_views.py::test_redisenio_no_conserva_familias_visuales_paralelas -q`

Expected: FAIL mientras quede al menos una regla o clase vieja.

- [ ] **Step 3: Resolver cada coincidencia productiva restante**

Run: `rg -n 'uni2-(ops|member|access)-|uni2-form-error-summary|uni2-record-list' templates static/css/uni2-design-system.css`

Para cada coincidencia:

- métricas → `uni2-metric-card-*`;
- paneles → `uni2-surface-card-*`;
- badges → `uni2-badge-*`;
- avatar → `uni2-avatar-*`;
- datos etiqueta/valor → `uni2-data-list`;
- acciones/layout → utilidades Bootstrap o `uni2-page-header-actions`;
- estilos CSS sin consumidor → eliminar.

No reemplazar una clase vieja por una clase nueva específica de pantalla.

- [ ] **Step 4: Revisar excepciones de dominio y CSS huérfano**

Run: `rg -n 'uni2-(cobro|period)-' templates static/css/uni2-design-system.css`

Conservar solo clases que tengan al menos un consumidor productivo y expresen selección/resumen de cobro o importes/generación de períodos. Eliminar selectores sin consumidor. Actualizar el inventario de `design-system-conceptos.md` para que coincida con el CSS final.

- [ ] **Step 5: Verificar límites cuantitativos y convenciones**

Run: `git diff --check`

Run: `git diff --numstat origin/staging...HEAD -- static/css/uni2-design-system.css`

Expected: la primera columna (líneas agregadas) es menor o igual que `500`.

Run: `rg -n '@media[^\n]*(max-width|min-width)' static/css/uni2-design-system.css`

Expected: no aparecen cortes nuevos distintos de `991.98px`, `767.98px` y `575.98px`.

- [ ] **Step 6: Ejecutar tests estructurales y hacer commit**

Run: `DB_ENGINE=sqlite uv run pytest web/tests/test_views.py -k 'design_system or catalogo or css or redisenio' -q`

Expected: PASS.

```bash
git add web/tests/test_views.py static/css/uni2-design-system.css templates especificacion/arquitectura/design-system-conceptos.md
git commit -m "Eliminar estilos paralelos del rediseño"
```

### Task 7: Verificar comportamiento y comparar visualmente

**Files:**
- Verify only: full repository
- Local artifact, do not commit: `docs/capturas/pr42-design-system-alineado/`
- Compare with local baseline: `docs/capturas/pr42-diseno-alumna/`

**Interfaces:**
- Consumes: implementación completa de Tasks 1–6 y las 16 capturas válidas de línea base.
- Produces: evidencia automatizada y visual para revisar el PR, sin archivos productivos adicionales.

- [ ] **Step 1: Ejecutar la suite completa con SQLite**

Run: `DB_ENGINE=sqlite uv run pytest -q`

Expected: `459 passed` o más; solo se admiten las dos advertencias preexistentes de Django 6 ya registradas.

- [ ] **Step 2: Confirmar que no hay cambios de persistencia ni errores de Django**

Run: `DB_ENGINE=sqlite uv run python manage.py makemigrations --check --dry-run`

Expected: `No changes detected`.

Run: `DB_ENGINE=sqlite uv run python manage.py check`

Expected: `System check identified no issues`.

- [ ] **Step 3: Preparar el mismo escenario ficticio de la línea base**

Usar la base local `test.sqlite3` y los mismos perfiles ficticios empleados en `docs/capturas/pr42-diseno-alumna/`: sesión administrativa aislada para las seis pantallas de gestión y sesión de asociado aislada para credencial/cuotas. No usar datos reales ni reutilizar cookies entre perfiles.

- [ ] **Step 4: Capturar las ocho vistas en ambos anchos**

Guardar en `docs/capturas/pr42-design-system-alineado/` los mismos nombres de la línea base:

```text
01-home-gestion-desktop.png       01-home-gestion-mobile.png
02-asociados-listado-desktop.png  02-asociados-listado-mobile.png
03-asociado-detalle-desktop.png   03-asociado-detalle-mobile.png
04-cobrar-cuotas-desktop.png      04-cobrar-cuotas-mobile.png
05-periodos-cuota-desktop.png     05-periodos-cuota-mobile.png
06-nuevo-asociado-desktop.png     06-nuevo-asociado-mobile.png
07-mi-credencial-desktop.png      07-mi-credencial-mobile.png
08-mis-cuotas-desktop.png         08-mis-cuotas-mobile.png
```

Usar viewport `1440` para desktop y `390` para mobile. Registrar HTTP 200 antes de cada captura; si aparece 403, descartar esa captura, iniciar el perfil correcto y repetirla.

- [ ] **Step 5: Revisar claro, oscuro, mobile y teclado**

Para cada pantalla anotar en el resumen del PR:

- mejora conservada;
- decoración simplificada;
- componente compartido usado;
- cambio de densidad/altura o scroll horizontal;
- resultado claro/oscuro;
- recorrido de foco por acciones, enlaces, formularios y checkboxes.

No agregar las imágenes al índice de Git.

- [ ] **Step 6: Revisar el diff final contra la especificación aprobada**

Run: `git diff --check origin/staging...HEAD`

Run: `git diff --stat origin/staging...HEAD`

Run: `git status --short`

Expected: sin errores de whitespace; solo capturas locales sin seguimiento; ningún cambio funcional o migración inesperada.

- [ ] **Step 7: Comprobar los commits de entrega**

Run: `git log --oneline origin/staging..HEAD`

Expected: la especificación, este plan y los commits en castellano de cada tarea aparecen separados y en orden revisable.
