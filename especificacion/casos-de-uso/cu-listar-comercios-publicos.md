---
type: "Caso de uso"
title: "CU-listar-comercios-publicos"
description: "Actor: Visitante"
tags: [mvp, caso-de-uso]
timestamp: 2026-06-22T00:00:00-03:00
status: "listo"
---

# CU-listar-comercios-publicos

**Actor:** Visitante

**Flujo principal:**

1.  Ingresa a la home.
2.  Selecciona el acceso a comercios adheridos.
3.  El sistema muestra los comercios publicados, ordenados por `orden`, con su actividad comercial y beneficio vigente.
4.  El visitante puede consultar los datos públicos de contacto o presencia web disponibles.

**Reglas relacionadas:** aplican todas las [reglas de comercios públicos](../reglas/comercios-publicos.md).

**Modelos afectados:** ActividadComercial, Comercio.
