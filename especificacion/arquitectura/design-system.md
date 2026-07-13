---
type: "Decisión de arquitectura"
title: "Design system interno"
description: "Referencia visual interna para construir pantallas de Uni2."
tags: [mvp, arquitectura, frontend]
timestamp: 2026-06-28T00:00:00-03:00
---

# Design system interno

El design system de Uni2 se sirve en `/design-system/` como una herramienta interna para desarrollo y mantenimiento visual.

La página requiere login y el permiso `gestion.ver_design_system`. El enlace aparece solo en el menú de usuario cuando la persona tiene ese permiso.

## Qué muestra

La vista reúne los patrones visuales que el equipo usa para construir pantallas en Django con Bootstrap: tokens, tipografía, componentes, bloques de home, secciones de servicios, beneficios, operaciones y una guía de partición para templates.

## Relación con la especificación

La especificación OKF describe alcance, reglas, casos de uso, pantallas y arquitectura funcional. El design system describe cómo deben verse y componerse esas pantallas.

Cuando una pantalla nueva o un rediseño necesita un patrón visual que todavía no existe, primero se define o documenta en el design system. Después se aplica en la pantalla concreta.

## Nombres de componentes

Los componentes sugeridos en el design system se nombran por patrón visual o responsabilidad de interfaz, no por entidad de negocio. Esto permite reutilizarlos en pantallas públicas, backoffice y experiencias autenticadas sin arrastrar nombres del ejemplo original.

## Relación entre Bootstrap, componentes UNI2 y catálogo

Bootstrap es la base técnica de maquetación y controles estándar. Se usa para grillas simples, formularios, tablas, dropdowns, collapse, botones operativos y utilidades responsive.

El CSS propio usa los mismos cortes responsive de Bootstrap: `991.98px` para adaptar navegación y composiciones amplias por debajo de `lg`, `767.98px` para apilar composiciones por debajo de `md` y `575.98px` para ajustes compactos por debajo de `sm`. No se mantienen breakpoints intermedios arbitrarios. Los valores se escriben como `max-width` con `0.02px` menos para no superponerse con el inicio del breakpoint de Bootstrap.

Los componentes visuales propios de Uni2 usan clases productivas con prefijo `uni2-` tanto en las pantallas reales como en el catálogo. Ejemplos: `uni2-hero`, `uni2-cta`, `uni2-section-heading`, `uni2-section-kicker`, `uni2-service-card`, `uni2-service-icon`, `uni2-benefit-band`, `uni2-benefit-mix-card`, `uni2-benefit-logo-cloud`, `uni2-benefit-logo-dot`, `uni2-ad-card`, `uni2-step-card`, `uni2-info-box`, `uni2-navbar` y `uni2-footer`.

La página interna `/design-system/` usa los componentes estándar de Bootstrap para su mobiliario documental: navegación, grillas, cards, badges, listas, espaciado, bordes y fondos. Esto evita mantener CSS propio para estructuras que Bootstrap ya resuelve y permite que el catálogo se concentre en mostrar los componentes propios de Uni2.

Las secciones completas y los agrupadores se presentan como bandas o bloques sin card. Una card se usa solamente cuando representa una unidad individual con límite propio: un elemento repetido, un formulario, una métrica o un ejemplo aislado. No se anidan cards; si un bloque agrupa varias unidades que ya tienen borde o superficie propios, el agrupador queda sin borde.

Cuando el catálogo muestra un componente que también existe en producción, debe usar la misma clase productiva `uni2-*` que usa la pantalla real. El catálogo no define clases `ds-*`: su mobiliario documental se resuelve con componentes y utilidades de Bootstrap.

Las clases genéricas sin prefijo, como `hero`, `cta`, `step`, `info-box`, `ad-card` o `benefit-card`, no deben usarse en pantallas productivas nuevas. Los componentes que el catálogo comparte con producción usan el prefijo `uni2-`.

La lista de beneficios con logo circular, metadata y descuento usa las mismas clases globales en el catálogo y en la pantalla productiva. El listado conserva una respuesta de hover y foco consistente para indicar que cada fila enlaza a una página de detalle. El MVP no usa modales por hash para este flujo.

Los datos de ejemplo pueden mencionar asociados, beneficios, servicios o cuotas porque pertenecen a Uni2. El nombre de un reusable nuevo no debe quedar atado a esos ejemplos salvo que sea una pieza realmente exclusiva de esa entidad.

## Forma de trabajo

Antes de crear una pantalla, el equipo debe identificar qué patrón del design system resuelve cada parte de la interfaz. Si el patrón existe, se reutiliza con datos del caso concreto. Si falta, se agrega primero al design system o se documenta junto con la pantalla que lo introduce.

Cuando se cree un template reusable nuevo, el nombre debe responder a esta pregunta: "qué patrón de interfaz es", no "para qué entidad lo usamos hoy".

Los templates reutilizables se separan en dos niveles:

- `templates/components/` contiene una unidad visual individual y no recorre colecciones de negocio. Por ejemplo, una tarjeta de servicio, una tarjeta de rubro o una publicidad.
- `templates/includes/` compone una sección, recorre los datos preparados por selectors y decide la grilla responsive o el destino de los enlaces.

El catálogo usa los mismos templates de `components/` que producción y aporta solamente datos demostrativos. No debe copiar manualmente el HTML interno de una tarjeta productiva.

Los componentes de chrome también pueden mostrarse dentro del catálogo usando su partial real. La muestra del footer incluye `includes/footer.html` y le pasa un identificador y un nombre de landmark propios para no duplicar el `id="contacto"` del footer global. En las páginas comunes, el include conserva `contacto` como valor por defecto.

## Chrome base

El chrome compartido de Django se organiza en `base.html`, `includes/navbar.html` e `includes/footer.html`.

La cabecera global contiene solo marca, navegación principal, acceso de usuario y entradas internas según permisos. No incluye horario de atención, WhatsApp, Instagram ni otros datos de contacto; esos contenidos viven en secciones específicas de la home, páginas de detalle o footer cuando correspondan.

El menú de usuario de la cabecera usa el componente productivo `uni2-user-menu`. Las opciones internas se agrupan como `Paneles`, `Herramientas` y `Cuenta` para diferenciar experiencias operativas, herramientas técnicas y salida de sesión.

En desktop, `uni2-user-menu` funciona como dropdown de Bootstrap. En mobile, las mismas entradas se muestran como enlaces directos dentro de la lista abierta por la hamburguesa, con el mismo comportamiento visual que "Productos y servicios" y "Comercios". Esto evita un segundo nivel de apertura y mantiene la navegación principal como una lista plana.

El cambio de tema no forma parte de la cabecera. Se muestra como botón flotante fijo abajo a la derecha, siguiendo el diseño visual base.

El tema se determina antes de cargar las hojas de estilo para evitar un destello del tema incorrecto. Si la persona no eligió un tema, se sigue `prefers-color-scheme`; solo una acción explícita sobre el botón se guarda en `localStorage`. El botón funciona como control conmutado mediante `aria-pressed` y mantiene un nombre accesible estable.

## Accesibilidad compartida

El chrome incluye un enlace para saltar directamente al contenido principal. Todos los enlaces, botones, controles de formulario y elementos con navegación por teclado reciben un anillo de foco visible mediante `--color-focus-ring`, con un valor de contraste específico para cada tema.

Las animaciones y transiciones respetan `prefers-reduced-motion`. En ese modo se eliminan los desplazamientos decorativos, el scroll deja de ser animado y los carruseles comienzan pausados.

El carrusel de publicidades ofrece controles anterior, pausa/reanudación y siguiente, además de indicadores con un área interactiva de `44px`. Puede recorrerse con las flechas del teclado cuando recibe foco, se pausa durante interacción con puntero, touch o teclado y no anuncia automáticamente cada cambio a lectores de pantalla. Cada publicidad informa su posición dentro del conjunto. Si hay una sola publicidad, no se muestran controles innecesarios.

## Breadcrumbs compartidos

El catálogo presenta `uni2-breadcrumbs` en la capa de componentes y usa el mismo partial productivo `templates/components/breadcrumbs.html` que las páginas de detalle.

El breadcrumb es un componente de navegación contextual, no una primitiva: combina una lista ordenada, enlaces, separadores y el estado de página actual dentro de un `nav` con nombre accesible. Usa la estructura base de Bootstrap, un separador textual decorativo `›`, enlaces con el color de acción y la página actual con color de texto secundario.

Se usa en páginas de detalle con rutas de dos o tres niveles. No se usa en la home ni en dashboards. La página actual no enlaza y declara `aria-current="page"`; los nombres largos pueden envolver en mobile. No se agrega un icono de inicio porque el texto ya comunica el destino y el separador no necesita exponerse a tecnologías asistivas.

El partial resuelve `Inicio` y su URL como valores por defecto. Las páginas pasan explícitamente `parent_url`, `parent_label` y `current_label`; también pueden reemplazar `home_url`, `home_label` y `aria_label` cuando una muestra o contexto lo necesita. Esta interfaz cubre la jerarquía corta del MVP sin introducir listas armadas en las views.

Las páginas de categoría, producto/servicio, comercio disponible y comercio no disponible usan este componente. Actividad comercial conserva la decisión específica de no mostrar breadcrumb.

## Alertas UNI2 compartidas

El catálogo y las pantallas productivas ubican las alertas en componentes, no en primitivos. Una alerta combina icono, variante semántica, título, mensaje y acción opcional; por eso no se trata como un valor visual aislado.

El componente `uni2-alert` usa una superficie legible, borde lateral con el color de estado, icono circular y diagonales institucionales de baja opacidad. Las variantes son `uni2-alert-info`, `uni2-alert-success`, `uni2-alert-warning` y `uni2-alert-danger`, usando solamente Bootstrap Icons.

Todas las alertas se renderizan mediante `templates/components/alert.html`, incluidos los mensajes del framework de Django. El partial acepta variante, título, mensaje, dos mensajes secundarios, nota, acción y clases de espaciado. Los bloques explicativos estáticos pasan `is_static=True` para no convertirse en regiones vivas.

Los mensajes globales de Django se agrupan en `uni2-flash-messages`, dentro del container de Bootstrap y con un ancho máximo de `960px`. Esto evita que una notificación breve se extienda por todo el viewport. Las alertas que forman parte del contenido de una pantalla conservan el ancho disponible de su sección.

`role="alert"` se reserva para errores urgentes; mensajes informativos, confirmaciones y advertencias no bloqueantes usan `role="status"`. Las explicaciones que ya están visibles al cargar la página no reciben un live region.

Las clases Bootstrap `alert` y `alert-*` ya no se usan en templates propios ni tienen overrides en la hoja de Uni2. Bootstrap sigue disponible como dependencia, pero la aplicación mantiene una sola presentación productiva de alertas.

## Tokens visibles en el catálogo

La sección de tokens de `/design-system/` muestra el inventario público completo: paleta de marca, roles de color, tipografía de títulos, radios, sombras, textura y movimiento. Los overrides `--bs-*` se documentan aparte como integración técnica con Bootstrap. Las variables locales de un componente, como `--card-color`, no forman parte del contrato global y no se presentan como tokens reutilizables.

El espaciado y las grillas responsive usan las escalas de Bootstrap. Uni2 no define una segunda escala de espaciado ni otros nombres para los mismos breakpoints.

## Alcance de esta decisión

Esta página es una referencia de trabajo, no una pantalla operativa del MVP. Su objetivo es ordenar decisiones visuales y hacerlas compartidas para que el proyecto siga siendo entendible para estudiantes que se suman después.
