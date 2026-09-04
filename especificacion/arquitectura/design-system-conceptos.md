# Design System Uni2 — Conceptos fundamentales

## 1. La pirámide

Un design system se organiza en capas. Cada capa usa solo lo que define la capa anterior.

```
        [ Páginas ]          vistas completas (home, dashboard, detalle)
       [ Patrones ]          secciones reutilizables (hero, benefit-band, price-table)
      [ Componentes ]        piezas con identidad propia (service-card, benefit-card, metric-card)
     [ Primitivos ]          elementos base sin semántica de negocio (botón, badge, input)
    [ Tokens ]               variables de diseño (colores, radios, sombras, tipografía)
```

La regla de trabajo es que cada capa se apoye en la anterior. Los componentes nuevos deben usar tokens para las decisiones compartidas y las páginas deben componerse con Bootstrap y clases `uni2-*`, evitando estilos inline salvo valores dinámicos inevitables.

---

## 2. Los tokens (dos capas)

El sistema diferencia la paleta de marca de los roles que consumen los componentes.

**Capa 1 — Paleta de marca:** valores concretos que identifican a Uni2.

```css
--brand-blue: #3f51b5;
--brand-yellow: #ffcb30;
--brand-green: #4ccb4a;
--brand-red: #ff2b2b;
```

**Capa 2 — Tokens de rol:** explican para qué se usa un valor.

```css
--color-action-primary: var(--brand-blue);
--color-action-on-surface: var(--brand-blue);
--color-success-text: #177323;
--color-warning-text: #765900;
--color-danger-text: var(--brand-red-dark);
--color-text: #1a1a2e;
--color-on-strong: #ffffff;
--color-on-bright: #1a1a2e;
--color-page: #f7f9fc;
--color-surface: #ffffff;
--color-border: #e0e0e0;
--radius-card: 12px;
--font-size-title-section: clamp(2.35rem, 6vw, 4.8rem);
--motion-duration-fast: 180ms;
```

El tema oscuro redefine los roles que deben cambiar, sin modificar la paleta institucional:

```css
[data-theme="dark"] {
  --color-action-on-surface: #97a6ff;
  --color-success-text: #76e875;
  --color-warning-text: #ffda63;
  --color-danger-text: #ff8d96;
  --color-text: #edf2ff;
  --color-page: #080c16;
  --color-surface: #101827;
  --color-border: #2a2a4a;
}
```

Los componentes usan tokens de rol para texto, fondos, bordes, radios, sombras, tipografía y movimiento. Las variantes que representan explícitamente los colores institucionales pueden usar tokens `--brand-*`.

`--color-action-primary` representa el fondo de una acción fuerte y no se usa automáticamente como texto. `--color-action-on-surface` representa enlaces, contornos e indicadores sobre una superficie; por eso cambia a un tono claro en el tema oscuro. Los tokens `--color-success-text`, `--color-warning-text` y `--color-danger-text` cumplen el mismo rol para estados semánticos. `--color-on-strong` aporta texto claro sobre fondos oscuros y `--color-on-bright` aporta texto oscuro sobre amarillos o verdes luminosos.

El espaciado y los cortes responsive no se duplican como tokens propios: se usa la escala de utilidades y los breakpoints de Bootstrap 5. Solo se agrega un token cuando representa una decisión compartida del producto; un valor aislado puede permanecer local al componente.

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
  font-size: var(--font-size-title-page);
  font-weight: var(--font-weight-title-display);
  letter-spacing: var(--letter-spacing-title-display);
  line-height: var(--line-height-title-display);
}

.uni2-titulo-seccion {
  font-size: var(--font-size-title-section);
  font-weight: var(--font-weight-title-display);
  letter-spacing: var(--letter-spacing-title-display);
  line-height: var(--line-height-title-display);
}

.uni2-titulo-componente {
  font-size: var(--font-size-title-component);
  font-weight: var(--font-weight-title-component);
  letter-spacing: var(--letter-spacing-title-component);
  line-height: var(--line-height-title-component);
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

`--brand-blue` no es un componente: es un valor de la paleta. `--color-action-primary` expresa el rol que ese valor cumple en botones y acciones principales.
`.uni2-titulo-seccion` no es un componente, es un tamaño que los componentes aplican a sus headings.

---

## 4. Cómo se construye un componente

Un componente tiene:
1. Una clase raíz con prefijo `uni2-` que lo identifica
2. Clases modificadoras para variantes de color o tamaño
3. Clases de elementos internos para partes del componente
4. Usa tokens para decisiones compartidas; un valor estrictamente local puede quedar dentro del componente

### Ejemplo: uni2-service-card

```css
/* Raíz del componente */
.uni2-service-card {
  background: var(--color-surface);   /* token semántico */
  border-top: 7px solid var(--card-color);
  box-shadow: var(--shadow-floating);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 260px;
  padding: 26px 24px;
}

/* Elemento interno: título */
.uni2-service-card h3 {
  color: var(--color-text);
  font-size: clamp(1.2rem, 2vw, 1.5rem);
  font-weight: 850;
  letter-spacing: -0.04em;
}

.uni2-service-card .link {
  color: var(--card-action);
}

/* Cada variante separa su color decorativo del color legible de la acción. */
.uni2-service-card-blue {
  --card-color: var(--brand-blue);
  --card-action: var(--color-action-on-surface);
}

.uni2-service-card-green {
  --card-color: var(--brand-green);
  --card-action: var(--color-success-text);
}
```

```html
<a class="uni2-service-card uni2-service-card-blue" href="/servicios/fotocopias/">
  <span class="uni2-service-icon"><i class="bi bi-files"></i></span>
  <div>
    <h3>Fotocopias</h3>
    <p>Blanco y negro, doble faz.</p>
  </div>
  <span class="link">Ver precios</span>
</a>
```

Una service card con destino usa un único enlace en la raíz: toda la superficie es interactiva y la etiqueta `.link` es texto, no un segundo enlace anidado. Cuando la card solo agrupa información o contiene acciones independientes, la raíz es un `article` o `div` con `uni2-service-card-static`; esa variante no se eleva al pasar el puntero.

### Convenciones de nomenclatura

| Tipo | Patrón | Ejemplo |
|---|---|---|
| Componente raíz | `uni2-[nombre]` | `uni2-service-card` |
| Modificador | `uni2-[nombre]-[variante]` | `uni2-service-card-blue` |
| Elemento interno | `uni2-[nombre]-[parte]` | `uni2-benefit-list-logo` |
| Patrón de página | `uni2-[nombre]` | `uni2-hero`, `uni2-benefit-band` |

---

## 5. Inventario de componentes actuales

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
| `uni2-skip-link` | Enlace de salto al contenido principal, visible al recibir foco |
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
| `uni2-section-heading` | Cabecera de sección con título + controles |

### Acciones

| Clase | Uso |
|---|---|
| `uni2-cta` | Botón principal amarillo |
| `uni2-cta-secondary` | Botón secundario azul |

### Formularios

| Clase | Uso |
|---|---|
| `uni2-field-error` | Mensaje compacto de validación junto al control; combina franja semántica, ícono y texto sin viñetas |
| `uni2-preinscription-result` | Card pública de confirmación con estado, mensaje, notas y acción responsive |

### Badges y etiquetas

| Clase | Uso |
|---|---|
| `uni2-badge` | Etiqueta amarilla tipo pill |
| `uni2-discount` | Descuento verde en cards de publicidad |

### Identidad y validación

| Clase | Uso |
|---|---|
| `uni2-credential-card` | Credencial institucional compartida por la vista online y la copia offline |
| `uni2-credential-brand` | Cabecera de marca con logo y denominación del documento |
| `uni2-credential-state` | Banda semántica inferior; combina color fuerte, símbolo y texto |
| `uni2-credential-technical` | Detalle secundario para el UUID de respaldo |
| `uni2-validation-station` | Puesto de control compartido por el ingreso manual y el resultado de una validación |
| `uni2-validation-spotlight` | Panel fuerte que comunica propósito o resultado con color, icono y texto |
| `uni2-validation-panel` | Superficie clara para el formulario o los datos permitidos |

### Servicios

| Clase | Uso |
|---|---|
| `uni2-service-card` | Card de servicio con borde superior de color |
| `uni2-service-card-static` | Variante informativa sin interacción sobre toda la superficie |
| `uni2-service-card-blue` | Variante azul |
| `uni2-service-card-green` | Variante verde |
| `uni2-service-card-yellow` | Variante amarilla |
| `uni2-service-card-red` | Variante roja |
| `uni2-service-card-purple` | Quinta variante; transitoriamente comparte la paleta roja |
| `uni2-service-icon` | Ícono dentro de la service card |
| `uni2-service-detail` | Layout de página pública de categoría |

### Navegación contextual

| Clase | Uso |
|---|---|
| `uni2-breadcrumbs` | Ruta compartida para páginas de detalle; se renderiza con `components/breadcrumbs.html` |

### Alertas

| Clase | Uso |
|---|---|
| `uni2-alert` | Mensaje compartido con icono, título y contenido |
| `uni2-alert-info` | Información general |
| `uni2-alert-success` | Confirmación de una operación |
| `uni2-alert-warning` | Revisión o atención necesaria |
| `uni2-alert-danger` | Error o acción bloqueada |
| `uni2-alert-icon` | Icono semántico circular |
| `uni2-alert-content` | Contenido textual de la alerta |
| `uni2-alert-title` | Título breve de la alerta |
| `uni2-alert-message` | Mensaje principal o secundario |
| `uni2-alert-note` | Nota separada al final |
| `uni2-alert-action` | Acción opcional |
| `uni2-flash-messages` | Agrupador de mensajes globales con ancho de lectura acotado |

### Publicidades (home carousel)

| Clase | Uso |
|---|---|
| `uni2-ad-card` | Card de publicidad con imagen de fondo |
| `uni2-ad-card-sin-foto` | Variante sin imagen |
| `uni2-carousel` | Carrusel horizontal |
| `uni2-carousel-heading` | Cabecera que acomoda los controles del carrusel en mobile |
| `uni2-carousel-controls` | Grupo de controles anterior, pausa y siguiente |
| `uni2-carousel-dot` | Indicador y acceso directo a una publicidad |
| `uni2-info-box` | Caja de info compacta |

### Beneficios — banda home

| Clase | Uso |
|---|---|
| `uni2-benefit-band` | Contenedor de la banda de beneficios |
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
| `uni2-benefit-page` | Fondo y espaciado de la página de actividad comercial |
| `uni2-benefit-page-layout` | Composición vertical del encabezado y el listado |
| `uni2-benefit-page-header` | Encabezado de la sección |
| `uni2-benefit-list` | Contenedor de la lista de comercios |
| `uni2-benefit-list-card` | Fila visual con acciones separadas |
| `uni2-benefit-list-logo` | Logo circular del comercio |
| `uni2-benefit-list-initials` | Variante de logo con iniciales de texto |
| `uni2-benefit-list-body` | Contenido de texto del item |
| `uni2-benefit-detail-link` | Nombre que enlaza al detalle del comercio |
| `uni2-benefit-online-link` | Acción que abre la presencia web |
| `uni2-benefit-meta` | Dirección e info secundaria |

### Horarios

| Clase | Uso |
|---|---|
| `uni2-hours-mobile` | Contenedor de horarios mobile |
| `uni2-hours-table` | Tabla de horarios desktop |
| `uni2-hours-table-compact` | Variante compacta usada en muestras o espacios acotados |
| `uni2-hours-day` | Fila de un día |
| `uni2-hours-chip` | Chip de turno horario |
| `uni2-hours-chip-blue` | Turno mañana |
| `uni2-hours-chip-green` | Turno tarde |
| `uni2-hours-chip-yellow` | Turno especial |
| `uni2-hours-chip-muted` | Cerrado / sin turno |

### Pasos

| Clase | Uso |
|---|---|
| `uni2-step-card` | Card de un paso individual |
| `uni2-step-card-blue` | Variante azul |
| `uni2-step-card-green` | Variante verde |
| `uni2-step-card-yellow` | Variante amarilla |
| `uni2-step-card-red` | Variante roja |
| `uni2-step-number` | Número del paso |

### Servicios (páginas de detalle — precios)

| Clase | Uso |
|---|---|
| `uni2-detail-page` | Fondo degradado de página de detalle |
| `uni2-detail-layout` | Grid de dos columnas |
| `uni2-detail-copy` | Columna de texto con heading display |
| `uni2-detail-panel` | Panel glassmorphism con borde azul superior |
| `uni2-category-detail-layout` | Flujo vertical de encabezado y catálogo de una categoría |
| `uni2-category-products-panel` | Contenedor de ancho completo para productos y servicios |
| `uni2-general-products-card` | Card neutral y de ancho completo para productos generales |
| `uni2-cycles-grid` | Grilla de cards de ciclos |
| `uni2-cycles-grid--multiple` | Variante de dos columnas en desktop ancho |
| `uni2-cycle-tabs` | Selector mobile de Ciclo Básico y Ciclo Superior |
| `uni2-cycle-tab` | Botón accesible de un ciclo |
| `uni2-cycle-section` | Sección principal de un ciclo |
| `uni2-cycle-card` | Card independiente de un ciclo |
| `uni2-cycle-card--cb` | Variante de Ciclo Básico con acento azul |
| `uni2-cycle-card--cs` | Variante de Ciclo Superior con acento verde |
| `uni2-cycle-heading` | Encabezado con abreviatura y nombre del ciclo |
| `uni2-course-group` | Grupo de productos para todo el ciclo o para un curso |
| `uni2-price-table-wrap` | Contenedor con scroll horizontal |
| `uni2-price-table` | Tabla de precios con estilo propio |
| `uni2-price-table-compact` | Variante sin min-width |
| `uni2-price-column` | Encabezado o celda monetaria alineada a la derecha |
| `uni2-print-contact` | Bloque de contacto con gradiente |
| `uni2-print-icon` | Ícono circular blanco dentro del bloque |
| `uni2-print-contact-body` | Texto del bloque, sin margen final y alineado con el ícono también en mobile |

### Comercios

| Clase | Uso |
|---|---|
| `uni2-commerce-detail` | Layout de página de detalle de comercio |
| `uni2-commerce-identity` | Agrupa logo e información principal del comercio |
| `uni2-commerce-identity-logo` | Logo circular junto al nombre del comercio |
| `uni2-commerce-identity-logo--fallback` | Variante sin imagen (iniciales) |
| `uni2-commerce-identity-copy` | Rubro, nombre y descripción del comercio |
| `uni2-commerce-benefit-block` | Bloque amarillo destacado del beneficio |
| `uni2-commerce-benefit-text` | Descripción del beneficio |
| `uni2-commerce-modal-dialog` | Ancho compacto del diálogo de comercio |
| `uni2-commerce-modal-card` | Composición centrada de la ficha modal |
| `uni2-commerce-modal-logo` | Logo circular principal del modal |
| `uni2-commerce-modal-logo--fallback` | Variante del logo con iniciales |
| `uni2-commerce-modal-benefit` | Beneficio amarillo debajo del logo |
| `uni2-commerce-modal-meta` | Datos públicos compactos y centrados |
| `uni2-commerce-modal-actions` | Acciones secundarias al pie del modal |

### Dashboard / Admin

| Clase | Uso |
|---|---|
| `uni2-dashboard-page` | Contexto de página de dashboard |
| `uni2-dashboard-pill` | Pill de contexto en el hero |
| `uni2-section-title-row` | Fila de título + acción de sección |
| `uni2-metric-card` | Resumen de un dato operativo real |
| `uni2-metric-card-{info,success,warning,danger}` | Variantes semánticas de una métrica |
| `uni2-metric-label` | Etiqueta de la métrica |
| `uni2-metric-value` | Valor de la métrica |
| `uni2-surface-card` | Card genérica para una unidad temática |
| `uni2-surface-card-{info,success,warning,danger}` | Variantes de acento semántico de una superficie |
| `uni2-badge-{info,success,warning,danger}` | Variantes semánticas de una etiqueta de estado |
| `uni2-avatar` | Imagen o iniciales que identifican a una persona |
| `uni2-avatar-{blue,green,yellow,red}` | Variantes cromáticas del avatar |
| `uni2-data-list` | Lista de pares etiqueta/valor para una ficha |
| `uni2-records-table` | Tabla que reorganiza sus registros como cards de dos columnas en mobile |
| `uni2-records-table-row` | Fila responsive informativa; puede combinarse con `uni2-clickable-row` cuando existe detalle |
| `uni2-timeline` | Secuencia cronológica vertical sin numeración visible |
| `uni2-timeline-item` | Evento conectado dentro de una línea de tiempo |
| `uni2-timeline-marker` | Punto del evento; el primero representa el movimiento más reciente |
| `uni2-page-header-actions` | Grupo de acciones del header de página |
| `uni2-pill-row` | Fila de pills |
| `uni2-schedule-card` | Card de horario/turno |

### Estructuras de flujos operativos

| Clase | Uso |
|---|---|
| `uni2-periods-table` | Ajuste de densidad de la tabla de períodos |
| `uni2-period-amounts` | Agrupa importe y recargos de un período |
| `uni2-period-generate-action` | Alinea cantidad y acción de generación de cuotas |
| `uni2-cobro-summary` | Distribuye los datos del asociado antes del cobro |
| `uni2-cobro-section` | Delimita la selección de cuotas dentro del formulario |
| `uni2-cobro-table` | Ancho mínimo de la tabla seleccionable de cuotas |
| `uni2-cobro-check` | Área visible y accesible del checkbox de una cuota |
| `uni2-cobro-fields` | Distribuye fecha, importe, método y observaciones |
| `uni2-cobro-field-full` | Hace que observaciones ocupe todo el ancho disponible |

Estas clases describen estructura exclusiva del flujo y no definen colores,
títulos, badges, cards ni acciones alternativas al sistema compartido.

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

- Repetir como literal una decisión de color que ya tiene token (`var(--brand-blue)` o un rol semántico)
- Crear una escala tipográfica paralela para títulos que ya cubren las clases `uni2-titulo-*`
- Asumir que está dentro de otro componente específico fuera de su propia raíz
- Depender de la posición en el DOM cuando una clase explícita comunica mejor la responsabilidad; los selectores estructurales quedan para relaciones internas breves y estables

---

## 6. Archivo CSS: estructura actual

Todo el sistema vive en `static/css/uni2-design-system.css`, cargado globalmente en `base.html`.

Las hojas históricas `uni2.css`, `uni2-v1.css` y `uni2-v2.css` fueron retiradas porque no se cargaban y duplicaban reglas antiguas. Las iteraciones no se conservan como archivos CSS paralelos: Git guarda el historial y la aplicación mantiene una sola hoja activa.

Orden interno del archivo:

```
:root (paleta + tokens de rol, tipografía y movimiento)
[data-theme="dark"] (overrides para tema oscuro)

Escala tipográfica (.uni2-titulo-*)
Section heading (.uni2-section-heading)
Benefit band (.uni2-benefit-band)

Hero (.uni2-hero, .uni2-hero-layout, .uni2-hero h1/p, .uni2-hero-actions)
CTA (.uni2-cta, .uni2-cta-secondary)
Badges y descuentos (.uni2-eyebrow, .uni2-badge, .uni2-discount)
Grillas de Bootstrap (.row y columnas responsive)
Service card (.uni2-service-card + variantes)
Service icon (.uni2-service-icon)
Step card / Info box (.uni2-step-card, .uni2-info-box)

Navbar (.uni2-navbar y partes)
Cards Bootstrap-custom
Botones y formularios (`uni2-field-error` para errores asociados a controles)
Footer (.uni2-footer y partes)
Theme toggle
Dashboard y gestión (.uni2-dashboard-page, .uni2-dashboard-pill, .uni2-metric-card, .uni2-surface-card)
Detail pages (.uni2-detail-*, .uni2-commerce-*, .uni2-price-table, .uni2-print-contact)
Benefit list (.uni2-benefit-list-*)

Media queries alineadas con los breakpoints de Bootstrap
```
