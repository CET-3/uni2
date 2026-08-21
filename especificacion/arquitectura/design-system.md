---
type: "Decisión de arquitectura"
title: "Design system interno"
description: "Referencia visual interna para construir pantallas de Uni2."
tags: [mvp, arquitectura, frontend]
timestamp: 2026-07-13T00:00:00-03:00
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

Las pantallas simples sin hero —por ejemplo login, credencial, cuotas y validación de credenciales— colocan su contenido dentro de `container py-5`. El container limita el ancho y mantiene el margen lateral en mobile; las filas y columnas internas deciden el ancho específico del formulario, card o tabla.

La página interna `/design-system/` usa los componentes estándar de Bootstrap para su mobiliario documental: navegación, grillas, cards, badges, listas, espaciado, bordes y fondos. Esto evita mantener CSS propio para estructuras que Bootstrap ya resuelve y permite que el catálogo se concentre en mostrar los componentes propios de Uni2.

Las secciones completas y los agrupadores se presentan como bandas o bloques sin card. Una card se usa solamente cuando representa una unidad individual con límite propio: un elemento repetido, un formulario, una métrica o un ejemplo aislado. No se anidan cards; si un bloque agrupa varias unidades que ya tienen borde o superficie propios, el agrupador queda sin borde.

Las métricas `uni2-metric-card` resumen un dato operativo real y conservan el detalle que permite interpretarlo en listas o tablas. Los modificadores `info`, `success`, `warning` y `danger` expresan su función semántica, no una decoración arbitraria. Los mismos acentos pueden aplicarse a `uni2-surface-card` para delimitar una unidad temática sin anidar cards.

La variante `uni2-surface-card-brand` identifica una unidad institucional mediante una franja fina azul, verde, amarilla y roja sobre una superficie neutra. La franja es decorativa y no comunica un estado; por eso no reemplaza los modificadores semánticos `info`, `success`, `warning` o `danger`.

El componente `uni2-compact-hero` encabeza una tarea operativa con una presencia menor que el hero principal: reúne contenido principal y acciones sobre una superficie neutra y reserva el extremo derecho para una geometría de colores institucionales plenos. No lleva descripción ni kicker. Puede incorporar `uni2-compact-hero-identity`, con un `uni2-compact-hero-avatar` alineado al nombre, y `uni2-compact-hero-summary` para un dato operativo prioritario sin anidar otra card. Cuando combina ambas zonas, `uni2-compact-hero-with-summary` reduce la geometría, apila las acciones en escritorio y usa `uni2-compact-hero-title` para limitar nombres largos a una escala aproximada de 32 a 48 px. Por debajo de `lg`, la geometría se convierte en una banda superior y el orden es contenido, resumen y acciones; los dos botones comparten fila mientras el ancho lo permite y se apilan por debajo de `sm`. Este componente convive con `uni2-surface-card-brand`; no la reemplaza ni modifica.

Los badges semánticos siempre incluyen un texto de estado y nunca comunican su significado solo mediante color. Las cuotas reutilizan `components/cuota_estado_badge.html`: `Pagada` usa `success` (verde), `Pendiente` usa `warning` (amarillo) y `Vencida` usa `danger` (rojo). El saldo se muestra como importe y no como un segundo badge, para que cada cuota tenga un único color de estado. Un valor no reconocido usa `info` como resguardo visual, sin asumir un estado del ciclo de vida. `uni2-avatar` representa una persona mediante imagen o iniciales, pero no es por sí mismo un control interactivo. `uni2-data-list` organiza pares etiqueta/valor de una ficha; cuando hay que comparar varias entidades o registros se usa una tabla.

Una tabla de resultados puede transformarse visualmente en registros apilados por debajo de `md` cuando mantener todas sus columnas produciría desplazamiento horizontal. Conserva un único markup y la semántica de tabla para tecnologías de asistencia: el encabezado queda oculto sólo visualmente y cada celda repite su etiqueta mediante `data-label`. La identidad ocupa el ancho completo, los demás datos se distribuyen en dos columnas y la fila mantiene una única zona interactiva.

Las clases `uni2-cobro-*` y `uni2-period-*` no forman una familia visual general: quedan limitadas a la estructura propia de selección/resumen del cobro y a la presentación/generación de períodos. Encabezados, colores, estados, métricas, superficies y acciones de esos flujos siguen usando los componentes compartidos.

Una `uni2-service-card` navegable usa un enlace como elemento raíz, de modo que toda la card tenga una única semántica y una única zona interactiva. La etiqueta visual `.link` dentro de esa raíz es un `span`. Una card informativa o con botones propios agrega `uni2-service-card-static`; no recibe hover de navegación y sus acciones conservan su semántica independiente.

Cuando el catálogo muestra un componente que también existe en producción, debe usar la misma clase productiva `uni2-*` que usa la pantalla real. El catálogo no define clases `ds-*`: su mobiliario documental se resuelve con componentes y utilidades de Bootstrap.

Las clases genéricas sin prefijo, como `hero`, `cta`, `step`, `info-box`, `ad-card` o `benefit-card`, no deben usarse en pantallas productivas nuevas. Los componentes que el catálogo comparte con producción usan el prefijo `uni2-`.

La lista de beneficios con logo circular, nombre, descripción, metadata y descuento usa las mismas clases globales en el catálogo y en la pantalla productiva. Un único enlace de detalle extiende su zona interactiva sobre toda la card mediante un pseudoelemento; `Visitar online` se posiciona por encima y conserva su destino externo independiente. Esto evita anidar enlaces y evita duplicar la acción de detalle en la navegación por teclado. El nombre y `Visitar online` no se subrayan; la descripción usa el color de texto secundario y el badge de beneficio se alinea a la derecha. En mobile, el componente usa dos columnas y ubica el badge debajo del contenido para preservar un ancho de lectura cómodo. La fila conserva una respuesta de hover y foco consistente. El MVP no usa modales por hash para este flujo.

La ficha modal de comercio tiene una presentación propia y no reutiliza el layout de la página completa. `uni2-commerce-modal-card` sigue la jerarquía compacta del prototipo aprobado: logo circular, beneficio amarillo, nombre, descripción y datos públicos breves centrados, con las acciones secundarias al pie. El diálogo limita su ancho a aproximadamente 520 px y reduce el logo en mobile. La carcasa continúa siendo el modal de Bootstrap para conservar cierre visible, `Escape`, fondo clickeable, scroll y restauración del foco; la página individual mantiene `uni2-commerce-detail` sin recibir estilos del modal.

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

El menú de usuario de la cabecera usa el componente productivo `uni2-user-menu`. Las opciones internas se agrupan como `Experiencias`, `Herramientas` y `Cuenta` para diferenciar las variantes de la home, las herramientas técnicas y la salida de sesión.

En desktop, `uni2-user-menu` funciona como dropdown de Bootstrap. En mobile, las mismas entradas se muestran como enlaces directos dentro de la lista abierta por la hamburguesa, con el mismo comportamiento visual que "Productos y servicios" y "Comercios". Esto evita un segundo nivel de apertura y mantiene la navegación principal como una lista plana.

El cambio de tema no forma parte de la cabecera. Se muestra como botón flotante fijo abajo a la derecha, siguiendo el diseño visual base.

El tema se determina antes de cargar las hojas de estilo para evitar un destello del tema incorrecto. Si la persona no eligió un tema, se sigue `prefers-color-scheme`; solo una acción explícita sobre el botón se guarda en `localStorage`. El botón funciona como control conmutado mediante `aria-pressed` y mantiene un nombre accesible estable.

## Accesibilidad compartida

El chrome incluye un enlace para saltar directamente al contenido principal. Todos los enlaces, botones, controles de formulario y elementos con navegación por teclado reciben un anillo de foco visible mediante `--color-focus-ring`, con un valor de contraste específico para cada tema.

Los colores institucionales no se usan directamente como texto cuando no alcanzan el contraste necesario. `--color-action-primary` y `--color-action-primary-hover` quedan reservados para fondos de acciones fuertes. Los enlaces, botones con contorno, encabezados interactivos e iconos sobre superficies usan `--color-action-on-surface`, que cambia a un tono más claro en el tema oscuro. Los textos de éxito, advertencia y error usan sus propios tokens semánticos para conservar al menos una relación de contraste de 4.5:1 sobre la superficie de cada tema.

Los componentes que alternan colores de marca también definen el color de su contenido. Los números de `uni2-step-card` usan fondo azul o rojo oscuro con texto claro, y fondo amarillo o verde con texto oscuro. Los chips de horario amarillos y verdes siguen el mismo criterio. El color de marca sigue visible en bordes y fondos, pero no decide por sí solo el color del texto.

En anchos menores a `md`, el contenido de `uni2-hero` se apoya sobre una superficie translúcida. Las diagonales institucionales permanecen como fondo, sin cruzarse visualmente con el texto ni depender de una posición particular del título o de la descripción.

Cuando una tabla contiene controles repetidos, cada control debe nombrar el dato de su fila. En el cobro de cuotas, cada checkbox tiene una etiqueta visualmente oculta con el período de la cuota; no se usa una etiqueta genérica como "Elegir" como único nombre accesible.

Las animaciones y transiciones respetan `prefers-reduced-motion`. En ese modo se eliminan los desplazamientos decorativos, el scroll deja de ser animado y los carruseles comienzan pausados.

El carrusel de publicidades ofrece controles anterior, pausa/reanudación y siguiente, además de indicadores con un área interactiva de `44px`. Puede recorrerse con las flechas del teclado cuando recibe foco, se pausa durante interacción con puntero, touch o teclado y no anuncia automáticamente cada cambio a lectores de pantalla. Cada publicidad informa su posición dentro del conjunto. Si hay una sola publicidad, no se muestran controles innecesarios.

## Breadcrumbs compartidos

El catálogo presenta `uni2-breadcrumbs` en la capa de componentes y usa el mismo partial productivo `templates/components/breadcrumbs.html` que las páginas de detalle.

El breadcrumb es un componente de navegación contextual, no una primitiva: combina una lista ordenada, enlaces, separadores y el estado de página actual dentro de un `nav` con nombre accesible. Usa la estructura base de Bootstrap, un separador textual decorativo `›`, enlaces con el color de acción y la página actual con color de texto secundario.

Se usa en páginas de detalle con rutas de dos o tres niveles. No se usa en la home. Nunca agrega `Inicio`: el logo ya cumple esa función global. La página actual no enlaza y declara `aria-current="page"`; los nombres largos pueden envolver en mobile. No se agrega un icono de inicio porque el texto ya comunica el destino y el separador no necesita exponerse a tecnologías asistivas.

## Formato monetario

Todo importe visible usa formato argentino, símbolo separado, punto de miles y
dos decimales: `$ 1.000,00`. La función compartida
`config.formatting.formatear_moneda()` es la fuente para textos Python y admin;
el filtro `moneda` de `web.templatetags.formatos` la reutiliza en templates.

Los valores técnicos de formularios, atributos `data-*`, planillas y payloads no
se convierten al formato visual: conservan el decimal que necesita su parser.
Esto evita que una mejora de presentación cambie cálculos o validaciones.

El partial recibe niveles explícitos: `root_url` y `root_label` para la raíz de sección; `ancestor_url` y `ancestor_label` para un nivel intermedio opcional; y `current_label` para la página actual. `aria_label` permite precisar el nombre accesible. No existen parámetros implícitos para `Inicio`, fragmentos o una página actual enlazada.

Las páginas de categoría, producto/servicio, actividad comercial, comercio disponible y comercio no disponible usan este componente. Sus jerarquías son `Productos y servicios > categoría`, `Productos y servicios > categoría > producto`, `Comercios > actividad` y `Comercios > actividad > comercio`.

En viewport de escritorio, las páginas públicas de detalle distribuyen introducción y panel en dos columnas mediante `uni2-detail-layout`. Por debajo de `lg` se apilan en una columna para mantener una lectura cómoda y evitar comprimir tablas o datos de contacto.

Las tablas de categorías usan `uni2-product-row` para convertir cada fila en
un único destino navegable mediante `uni2-product-row-link`. El enlace extiende
su área interactiva sin duplicarse en la navegación por teclado y la fila
responde a hover y `focus-within`. `uni2-product-thumb` integra la foto dentro
de la celda del nombre, por lo que un producto sin foto no deja una columna
vacía. Los escenarios comerciales se distinguen con encabezados de tabla y
`uni2-price-badge`, no solamente por color.

La ficha individual usa `uni2-product-photo` para la imagen completa y
`uni2-product-recipient` para ciclo y curso. La imagen compartida de categoría
usa `uni2-informative-image` tanto en categoría como en producto. Todas estas
regiones son opcionales y desaparecen por completo cuando no tienen datos.

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
