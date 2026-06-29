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

El cambio de tema no forma parte de la cabecera. Se muestra como botón flotante fijo abajo a la derecha, siguiendo el diseño visual base.

## Alcance de esta decisión

Esta página es una referencia de trabajo, no una pantalla operativa del MVP. Su objetivo es ordenar decisiones visuales y hacerlas compartidas para que el proyecto siga siendo entendible para estudiantes que se suman después.
