# Design System Uni2 — Conceptos fundamentales

## 1. La pirámide

Un design system se organiza en capas. Cada capa usa solo lo que define la capa anterior.

```
        [ Páginas ]          vistas completas (home, dashboard, detalle)
       [ Patrones ]          secciones reutilizables (hero, benefit-band, price-table)
      [ Componentes ]        piezas con identidad propia (service-card, metric, status)
     [ Primitivos ]          elementos base sin semántica de negocio (botón, badge, input)
    [ Tokens ]               variables de diseño (colores, radios, sombras, tipografía)
```

La regla es: **una capa no puede saltear niveles**. Un componente usa tokens, no valores mágicos. Una página usa patrones y componentes, no estilos inline.

---

## 2. Los tokens (dos capas)

El sistema tiene dos niveles de variables CSS:

**Capa 1 — Tokens base** (valores concretos, no se usan directamente en componentes):

```css
--primary: #3f51b5;
--bg:      #ffffff;
--text:    #1a1a2e;
--radius:  12px;
```

**Capa 2 — Tokens semánticos** (nombrados por su rol, los componentes los usan siempre):

```css
--azul:   var(--primary);
--texto:  var(--text);
--fondo:  var(--bg-alt);
--radio:  24px;
```

El tema oscuro solo redefine los tokens base:

```css
[data-theme="dark"] {
  --bg:   #1a1a2e;
  --text: #eaeaea;
}
```

Los tokens semánticos (`--texto`, `--fondo`, etc.) heredan el cambio automáticamente porque apuntan a los base con `var()`. Los componentes nunca necesitan saber si el tema es claro u oscuro.

---

## 3. Tipografía: clases de escala, no estilos en h1/h2/h3

### El problema de estilar los elementos HTML directamente

Si escribís:

```css
h1 { font-size: clamp(3.2rem, 8vw, 6.6rem); font-weight: 900; }
h2 { font-size: clamp(1.8rem, 3.5vw, 2.6rem); }
```

Eso afecta **todos los h1 y h2 del sitio**, incluyendo los que están dentro de cards, paneles, tablas y navbars donde ese tamaño es incorrecto. Rompe los componentes que ya tienen sus propios estilos tipográficos.

### La solución: clases de escala tipográfica

El sistema define clases utilitarias para cada nivel de la jerarquía visual:

```css
.uni2-titulo-principal {
  font-size: clamp(3.2rem, 8vw, 6.6rem);
  font-weight: 900;
  letter-spacing: -0.04em;
  line-height: 1;
}

.uni2-titulo-seccion {
  font-size: clamp(2.35rem, 6vw, 4.8rem);
  font-weight: 900;
  letter-spacing: -0.04em;
  line-height: 1;
}

.uni2-titulo-componente {
  font-size: clamp(1.2rem, 2vw, 1.5rem);
  font-weight: 850;
  letter-spacing: -0.04em;
  line-height: 1.08;
}
```

Y se aplican explícitamente en los templates:

```html
<!-- El h1 sigue siendo h1 semánticamente (accesibilidad, SEO) -->
<!-- La clase controla el look visual -->
<h1 class="uni2-titulo-principal">Mutual UNI2</h1>
<h2 class="uni2-titulo-seccion">Club de Beneficios</h2>
<h3 class="uni2-titulo-componente">Fotocopias</h3>
```

### Por qué separar semántica de estilo

- Un `h2` dentro de una card de dashboard necesita verse chico (16px).
- Un `h2` en la sección de beneficios necesita verse grande (40px+).
- Ambos son semánticamente `h2` (estructura de documento), pero visualmente distintos.
- La clase tipográfica resuelve el visual; la etiqueta HTML resuelve la jerarquía.

### Analogía con los tokens de color

`--azul` no es un componente, es un valor que los componentes usan.
`.uni2-titulo-seccion` no es un componente, es un tamaño que los componentes aplican a sus headings.

---

## 4. Cómo se construye un componente

Un componente tiene:
1. Una clase raíz con prefijo `uni2-` que lo identifica
2. Clases modificadoras para variantes de color o tamaño
3. Clases de elementos internos para partes del componente
4. Solo usa tokens semánticos (capa 2), nunca valores hardcodeados

### Ejemplo: uni2-service-card

```css
/* Raíz del componente */
.uni2-service-card {
  background: var(--surface-solid);   /* token semántico */
  border-top: 7px solid var(--card-color);
  box-shadow: var(--sombra);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 260px;
  padding: 26px 24px;
}

/* Elemento interno: título */
.uni2-service-card h3 {
  color: var(--texto);
  font-size: clamp(1.2rem, 2vw, 1.5rem);
  font-weight: 850;
  letter-spacing: -0.04em;
}

/* Modificadores de color (la variable --card-color la setea cada variante) */
.uni2-service-card-blue   { --card-color: var(--azul); }
.uni2-service-card-green  { --card-color: var(--verde); }
.uni2-service-card-yellow { --card-color: var(--amarillo); }
.uni2-service-card-red    { --card-color: var(--rojo); }
```

```html
<article class="uni2-service-card uni2-service-card-blue">
  <span class="uni2-service-icon"><i data-lucide="copy"></i></span>
  <div>
    <h3>Fotocopias</h3>
    <p>Blanco y negro, doble faz.</p>
  </div>
  <a class="link" href="/servicios/fotocopias/">Ver precios</a>
</article>
```

### Convenciones de nomenclatura

| Tipo | Patrón | Ejemplo |
|---|---|---|
| Componente raíz | `uni2-[nombre]` | `uni2-service-card` |
| Modificador | `uni2-[nombre]-[variante]` | `uni2-service-card-blue` |
| Elemento interno | `uni2-[nombre]-[parte]` | `uni2-benefit-list-logo` |
| Patrón de página | `uni2-[nombre]` | `uni2-hero`, `uni2-benefit-band` |

---

## 6. Inventario de componentes actuales

### Tipografía

| Clase | Uso |
|---|---|
| `uni2-titulo-principal` | Título de hero / portada |
| `uni2-titulo-seccion` | Título de sección |
| `uni2-titulo-componente` | Título de card o panel |
| `uni2-eyebrow` | Sobre-título decorativo amarillo |
| `uni2-section-kicker` | Etiqueta chica sobre un heading |
| `uni2-muted-kicker` | Etiqueta chica en tono suave |

### Navegación

| Clase | Uso |
|---|---|
| `uni2-navbar` | Barra de navegación principal |
| `uni2-navbar-inner` | Contenedor interno del navbar |
| `uni2-navbar-nav` | Lista de links de nav |
| `uni2-login-button` | Botón de login en navbar |
| `uni2-menu-button` | Botón hamburguesa mobile |
| `uni2-mobile-nav-button` | Variante mobile del botón de nav |
| `uni2-user-menu` | Dropdown del usuario logueado |
| `uni2-user-menu-button` | Botón que abre el user menu |
| `uni2-user-menu-section` | Grupo de items dentro del menú |
| `uni2-user-menu-label` | Etiqueta de sección del menú |
| `uni2-user-menu-link` | Link individual del menú |
| `uni2-user-menu-logout` | Link de cierre de sesión |

### Hero / Cabecera

| Clase | Uso |
|---|---|
| `uni2-hero` | Sección hero con gradiente de fondo |
| `uni2-hero-layout` | Contenedor interno del hero (z-index) |
| `uni2-hero-actions` | Grupo de CTAs del hero |
| `uni2-mini-hero` | Variante compacta del hero |
| `uni2-section-heading` | Cabecera de sección con título + controles |
| `uni2-section-inner` | Contenedor centrado max-width 1180px |

### Acciones

| Clase | Uso |
|---|---|
| `uni2-cta` | Botón principal amarillo |
| `uni2-cta-secondary` | Botón secundario azul |

### Badges y etiquetas

| Clase | Uso |
|---|---|
| `uni2-badge` | Etiqueta amarilla tipo pill |
| `uni2-discount` | Descuento verde en cards de publicidad |
| `uni2-discount-tag` | Descuento verde compacto en listas |
| `uni2-status` | Estado con variantes de color |
| `uni2-status-active` | Modificador: activo (verde) |
| `uni2-status-inactive` | Modificador: inactivo (gris) |
| `uni2-status-pending` | Modificador: pendiente (amarillo) |
| `uni2-status-overdue` | Modificador: vencido (rojo) |
| `uni2-status-paid` | Modificador: pagado (azul) |
| `uni2-status-badge-soft` | Badge suave estilo pill azul |

### Servicios

| Clase | Uso |
|---|---|
| `uni2-service-grid` | Grilla de 4 columnas para service cards |
| `uni2-service-card` | Card de servicio con borde superior de color |
| `uni2-service-card-blue` | Variante azul |
| `uni2-service-card-green` | Variante verde |
| `uni2-service-card-yellow` | Variante amarilla |
| `uni2-service-card-red` | Variante roja |
| `uni2-service-card-purple` | Variante violeta |
| `uni2-service-icon` | Ícono dentro de la service card |
| `uni2-service-detail` | Layout de página pública de categoría |

### Publicidades (home carousel)

| Clase | Uso |
|---|---|
| `uni2-ad-card` | Card de publicidad con imagen de fondo |
| `uni2-ad-card-sin-foto` | Variante sin imagen |
| `uni2-carousel` | Carrusel horizontal |
| `uni2-info-box` | Caja de info compacta |

### Beneficios — banda home

| Clase | Uso |
|---|---|
| `uni2-benefit-band` | Contenedor de la banda de beneficios |
| `uni2-benefit-intro` | Encabezado de la banda |
| `uni2-benefit-links` | Grilla de tarjetas de rubros |
| `uni2-benefit-mix-card` | Card de rubro con logos de comercios |
| `uni2-benefit-food` | Variante gastronomía |
| `uni2-benefit-sport` | Variante deporte |
| `uni2-benefit-beauty` | Variante belleza |
| `uni2-benefit-fashion` | Variante indumentaria |
| `uni2-benefit-logo-cloud` | Grupo de logos superpuestos |
| `uni2-benefit-logo-dot` | Logo circular individual |
| `uni2-benefit-logo-dot-left` | Posición izquierda |
| `uni2-benefit-logo-dot-main` | Posición central (más grande) |
| `uni2-benefit-logo-dot-right` | Posición derecha |
| `uni2-benefit-rubric` | Nombre del rubro en la card |

### Beneficios — lista de detalle

| Clase | Uso |
|---|---|
| `uni2-benefit-page` | Sección de lista de beneficios (fondo especial) |
| `uni2-benefit-page-header` | Encabezado de la sección |
| `uni2-benefit-back` | Link de volver atrás |
| `uni2-benefit-list` | Contenedor de la lista de comercios |
| `uni2-benefit-list-card` | Item clickeable de la lista |
| `uni2-benefit-list-logo` | Logo circular del comercio |
| `uni2-benefit-list-initials` | Variante de logo con iniciales de texto |
| `uni2-benefit-list-body` | Contenido de texto del item |
| `uni2-benefit-meta` | Dirección e info secundaria |
| `uni2-benefit-modal` | Modal por hash del detalle de comercio |
| `uni2-benefit-modal-backdrop` | Fondo clickeable del modal |
| `uni2-benefit-modal-card` | Contenido del modal |

### Métricas

| Clase | Uso |
|---|---|
| `uni2-metric-grid` | Grilla de métricas grandes |
| `uni2-metric` | Métrica grande individual |
| `uni2-metric-blue` | Variante azul |
| `uni2-metric-green` | Variante verde |
| `uni2-metric-yellow` | Variante amarilla |
| `uni2-metric-red` | Variante roja |
| `uni2-trend` | Indicador de tendencia |
| `uni2-trend-down` | Variante tendencia negativa |
| `uni2-trend-muted` | Variante tendencia neutral |
| `uni2-compact-metric-grid` | Grilla de métricas compactas |
| `uni2-compact-metric` | Métrica compacta individual |
| `uni2-compact-blue` | Variante azul compacta |
| `uni2-compact-green` | Variante verde compacta |
| `uni2-compact-yellow` | Variante amarilla compacta |
| `uni2-compact-red` | Variante roja compacta |
| `uni2-compact-icon` | Ícono dentro de métrica compacta |
| `uni2-compact-body` | Texto dentro de métrica compacta |

### Horarios

| Clase | Uso |
|---|---|
| `uni2-hours-mobile` | Contenedor de horarios mobile |
| `uni2-hours-table` | Tabla de horarios desktop |
| `uni2-hours-table-compact` | Variante compacta |
| `uni2-hours-day` | Fila de un día |
| `uni2-hours-chip` | Chip de turno horario |
| `uni2-hours-chip-blue` | Turno mañana |
| `uni2-hours-chip-green` | Turno tarde |
| `uni2-hours-chip-yellow` | Turno especial |
| `uni2-hours-chip-muted` | Cerrado / sin turno |

### Pasos

| Clase | Uso |
|---|---|
| `uni2-steps` | Grilla de pasos |
| `uni2-step-card` | Card de un paso individual |
| `uni2-step-card-blue` | Variante azul |
| `uni2-step-card-green` | Variante verde |
| `uni2-step-card-yellow` | Variante amarilla |
| `uni2-step-card-red` | Variante roja |
| `uni2-step-number` | Número del paso |

### Filtros

| Clase | Uso |
|---|---|
| `uni2-filter-bar` | Barra de filtros |
| `uni2-filter-chip` | Chip individual de filtro |
| `uni2-chip-row` | Fila de chips |

### Actividad

| Clase | Uso |
|---|---|
| `uni2-activity-list` | Lista de actividad reciente |
| `uni2-activity-item` | Item individual de actividad |
| `uni2-activity-icon` | Ícono del item de actividad |

### Servicios (páginas de detalle — precios)

| Clase | Uso |
|---|---|
| `uni2-detail-page` | Fondo degradado de página de detalle |
| `uni2-detail-layout` | Grid de dos columnas |
| `uni2-detail-copy` | Columna de texto con heading display |
| `uni2-detail-panel` | Panel glassmorphism con borde azul superior |
| `uni2-price-table-wrap` | Contenedor con scroll horizontal |
| `uni2-price-table` | Tabla de precios con estilo propio |
| `uni2-price-table-compact` | Variante sin min-width |
| `uni2-print-contact` | Bloque de contacto con gradiente |
| `uni2-print-icon` | Ícono circular blanco dentro del bloque |
| `uni2-contact-links` | Links de contacto (mail / whatsapp) |
| `uni2-contact-separator` | Separador "o" entre links |

### Comercios

| Clase | Uso |
|---|---|
| `uni2-commerce-detail` | Layout de página de detalle de comercio |
| `uni2-commerce-benefit-row` | Fila de beneficio en detalle |
| `uni2-commerce-benefit-logo` | Logo circular del comercio |
| `uni2-commerce-benefit-logo--fallback` | Variante sin imagen (iniciales) |
| `uni2-commerce-benefit-copy` | Texto del beneficio |
| `uni2-commerce-benefit-text` | Descripción del beneficio en mayúsculas |

### Dashboard / Admin

| Clase | Uso |
|---|---|
| `uni2-dashboard-page` | Contexto de página de dashboard |
| `uni2-dashboard-hero` | Hero compacto del dashboard |
| `uni2-dashboard-pill` | Pill de contexto en el hero |
| `uni2-dashboard-actions-grid` | Grilla de acciones rápidas |
| `uni2-admin-layout` | Grid de dos columnas (principal + sidebar) |
| `uni2-admin-main-column` | Columna principal |
| `uni2-admin-side-column` | Sidebar sticky |
| `uni2-quick-action-card` | Card de acción rápida |
| `uni2-quick-action-meta` | Metadata de la acción rápida |
| `uni2-module-card` | Card de módulo colapsable |
| `uni2-module-link-list` | Lista de links dentro de un módulo |
| `uni2-module-link-item` | Link individual del módulo |
| `uni2-module-link-copy` | Texto del link (título + descripción) |
| `uni2-module-toggle` | Botón de colapsar/expandir módulo |
| `uni2-module-toggle-label` | Label del toggle |
| `uni2-section-card` | Card de sección del dashboard |
| `uni2-section-title-row` | Fila de título + acción de sección |
| `uni2-sidebar-card` | Card del sidebar con list-group |
| `uni2-metric-card` | Card de métrica del dashboard |
| `uni2-metric-label` | Etiqueta de la métrica |
| `uni2-metric-value` | Valor de la métrica |
| `uni2-surface-card` | Card genérica sin borde |
| `uni2-info-card` | Card informativa |
| `uni2-page-header-actions` | Grupo de acciones del header de página |
| `uni2-mobile-stack-actions` | Acciones apiladas en mobile |
| `uni2-pill-row` | Fila de pills |
| `uni2-compact-list` | Lista con espaciado reducido |
| `uni2-support-link-list` | Lista de links de soporte |
| `uni2-support-link-item` | Item de link de soporte |
| `uni2-support-link-copy` | Texto del link de soporte |
| `uni2-progress` | Barra de progreso |
| `uni2-schedule-card` | Card de horario/turno |
| `uni2-inline-stack` | Elementos inline apilables |

### Footer

| Clase | Uso |
|---|---|
| `uni2-footer` | Footer del sitio |
| `uni2-footer-container` | Contenedor centrado del footer |
| `uni2-footer-actions` | Grupo de iconos de contacto |
| `uni2-footer-icon` | Ícono circular de contacto |
| `uni2-footer-icon-mail` | Variante mail (rojo) |
| `uni2-footer-icon-whatsapp` | Variante WhatsApp (verde) |
| `uni2-footer-icon-instagram` | Variante Instagram (amarillo) |
| `uni2-footer-location` | Dirección física |
| `uni2-footer-copy` | Texto de copyright |

---

> **Nota:** las clases marcadas en la columna "Uso" como variantes de color o posición son modificadores — se usan siempre junto a la clase raíz del componente.

### Lo que un componente NO debe hacer

- Usar colores literales (`#3f51b5`) en lugar de tokens (`var(--azul)`)
- Definir su propio `font-size` sin relación con la escala tipográfica
- Asumir que está dentro de otro componente específico
- Depender de la posición en el DOM (no usar `>` o `:first-child` salvo necesidad real)

---

## 5. Archivo CSS: estructura actual

Todo el sistema vive en `static/css/uni2-design-system.css`, cargado globalmente en `base.html`.

Orden interno del archivo:

```
:root (tokens base + tokens semánticos)
[data-theme="dark"] (overrides para tema oscuro)

Escala tipográfica (.uni2-titulo-*)
Section heading (.uni2-section-heading)
Benefit band (.uni2-benefit-band)

Layout helpers (.uni2-section-inner)
Hero (.uni2-hero, .uni2-hero-layout, .uni2-hero h1/p, .uni2-hero-actions)
CTA (.uni2-cta, .uni2-cta-secondary)
Badges y descuentos (.uni2-eyebrow, .uni2-badge, .uni2-discount, .uni2-discount-tag)
Grids (.uni2-service-grid, .uni2-metric-grid, .uni2-steps, .uni2-benefit-links)
Service card (.uni2-service-card + variantes)
Service icon (.uni2-service-icon)
Step card / Info box (.uni2-step-card, .uni2-info-box)

Navbar (.uni2-navbar y partes)
Cards Bootstrap-custom
Botones y formularios
Footer (.uni2-footer y partes)
Theme toggle
Dashboard components (.uni2-dashboard-*, .uni2-admin-*, .uni2-module-*, etc.)
Detail pages (.uni2-detail-*, .uni2-commerce-*, .uni2-price-table, .uni2-print-contact)
Benefit list (.uni2-benefit-list-*, .uni2-benefit-page)

Media queries (max-width: 1080px, 880px, 640px, etc.)
```
