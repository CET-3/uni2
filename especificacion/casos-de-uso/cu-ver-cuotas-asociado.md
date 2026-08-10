---
type: "Caso de uso"
title: "CU-ver-cuotas-asociado"
description: "Actor: Gestión con permiso para consultar asociados."
tags: [mvp, caso-de-uso]
timestamp: 2026-06-22T00:00:00-03:00
---

# CU-ver-cuotas-asociado

**Actor:** Gestión con permiso para consultar asociados.

**Alcance:** pantalla de lectura que muestra todas las cuotas del asociado, sin filtrar por estado. La ruta y el permiso se conservan temporalmente, pero la pantalla no tiene acceso desde el detalle mientras se diseña la consulta de cuotas.

**Flujo principal:**

1.  Un usuario autorizado abre directamente la ruta histórica de un asociado.
2.  El sistema muestra el historial completo de cuotas, ordenado del período más reciente al más antiguo.
3.  La pantalla conserva el contexto del asociado y muestra la deuda total acumulada.

**Modelos afectados:** Asociado, Cuota, PeríodoCuota.
