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

## Alcance de esta decisión

Esta página es una referencia de trabajo, no una pantalla operativa del MVP. Su objetivo es ordenar decisiones visuales y hacerlas compartidas para que el proyecto siga siendo entendible para estudiantes que se suman después.
