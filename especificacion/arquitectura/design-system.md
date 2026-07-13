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

Los componentes visuales propios de Uni2 usan clases productivas con prefijo `uni2-` tanto en las pantallas reales como en el catálogo. Ejemplos: `uni2-hero`, `uni2-cta`, `uni2-section-inner`, `uni2-section-heading`, `uni2-section-kicker`, `uni2-section-copy`, `uni2-service-grid`, `uni2-service-card`, `uni2-service-icon`, `uni2-benefit-band`, `uni2-benefit-links`, `uni2-benefit-mix-card`, `uni2-benefit-logo-cloud`, `uni2-benefit-logo-dot`, `uni2-ad-card`, `uni2-steps`, `uni2-step-card`, `uni2-info-box`, `uni2-navbar` y `uni2-footer`.

La página interna `/design-system/` usa los componentes estándar de Bootstrap para su mobiliario documental: navegación, grillas, cards, badges, listas, espaciado, bordes y fondos. Esto evita mantener CSS propio para estructuras que Bootstrap ya resuelve y permite que el catálogo se concentre en mostrar los componentes propios de Uni2.

Las secciones completas y los agrupadores se presentan como bandas o bloques sin card. Una card se usa solamente cuando representa una unidad individual con límite propio: un elemento repetido, un formulario, una métrica o un ejemplo aislado. No se anidan cards; si un bloque agrupa varias unidades que ya tienen borde o superficie propios, el agrupador queda sin borde.

La clase `ds-page` se reserva para la página interna `/design-system/`. Sirve como marco documental del catálogo: navegación propia, secciones de explicación, previews y tarjetas de referencia. Las páginas productivas no deben depender de `ds-page` para que un componente se vea correctamente.

Cuando el catálogo muestra un componente que también existe en producción, debe usar la misma clase productiva `uni2-*` que usa la pantalla real. `ds-page` es la única clase con prefijo `ds-*`; no se crean variantes como `ds-card`, `ds-kicker`, `ds-heading` o `ds-preview` porque esas responsabilidades se resuelven con Bootstrap.

Las clases genéricas sin prefijo, como `hero`, `cta`, `step`, `info-box`, `ad-card`, `benefit-card` o `section-inner`, no deben usarse en pantallas productivas nuevas. Si el catálogo conserva un nombre genérico para una pieza exclusivamente documental, su estilo debe quedar acotado por `.ds-page`; los componentes que comparte con producción usan el prefijo `uni2-`.

Algunos patrones históricos del catálogo, como la lista de beneficios con logo circular, metadata y descuento en un único badge visible, pueden compartirse con pantallas productivas siempre que se les expongan selectores globales equivalentes. En esos casos la vista interna sigue siendo la referencia visual, pero la implementación real no depende de `.ds-page` para renderizar correctamente. El listado compartido conserva una respuesta de hover/foco consistente: borde más marcado, elevación leve y sombra reforzada para indicar que cada fila es clickeable.

Ejemplos de nombres esperados:

- `components/media_list_item.html`: item de listado con imagen o logo, título, descripción, metadata y etiqueta destacada.
- `components/action_card.html`: card de acceso con ícono, título, descripción y link.
- `components/comparison_table.html`: tabla para comparar columnas de valores, estados o condiciones.
- `components/filter_bar.html`: búsqueda, selects, rango de fecha, chips activos y acción de limpiar.
- `components/metric_card.html`: indicador con número, contexto y color semántico.
- `forms/entity_form.html`: formulario Django renderizado con Bootstrap y mensajes de validación.
- `sections/action_grid.html`: grilla de accesos principales.
- `sections/feature_strip.html`: bloque destacado de features, categorías o beneficios.

Los datos de ejemplo pueden mencionar asociados, beneficios, servicios o cuotas porque pertenecen a Uni2. El nombre del componente no debe quedar atado a esos ejemplos salvo que sea una pieza realmente exclusiva de esa entidad.

## Forma de trabajo

Antes de crear una pantalla, el equipo debe identificar qué patrón del design system resuelve cada parte de la interfaz. Si el patrón existe, se reutiliza con datos del caso concreto. Si falta, se agrega primero al design system o se documenta junto con la pantalla que lo introduce.

Cuando se cree un template reusable nuevo, el nombre debe responder a esta pregunta: "qué patrón de interfaz es", no "para qué entidad lo usamos hoy".

## Chrome base

El chrome compartido de Django se organiza en `base.html`, `includes/navbar.html` e `includes/footer.html`.

La cabecera global contiene solo marca, navegación principal, acceso de usuario y entradas internas según permisos. No incluye horario de atención, WhatsApp, Instagram ni otros datos de contacto; esos contenidos viven en secciones específicas de la home, páginas de detalle o footer cuando correspondan.

El menú de usuario de la cabecera usa el componente productivo `uni2-user-menu`. Las opciones internas se agrupan como `Paneles`, `Herramientas` y `Cuenta` para diferenciar experiencias operativas, herramientas técnicas y salida de sesión.

En desktop, `uni2-user-menu` funciona como dropdown de Bootstrap. En mobile, las mismas entradas se muestran como enlaces directos dentro de la lista abierta por la hamburguesa, con el mismo comportamiento visual que "Productos y servicios" y "Comercios". Esto evita un segundo nivel de apertura y mantiene la navegación principal como una lista plana.

El cambio de tema no forma parte de la cabecera. Se muestra como botón flotante fijo abajo a la derecha, siguiendo el diseño visual base.

## Alcance de esta decisión

Esta página es una referencia de trabajo, no una pantalla operativa del MVP. Su objetivo es ordenar decisiones visuales y hacerlas compartidas para que el proyecto siga siendo entendible para estudiantes que se suman después.
