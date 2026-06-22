---
type: "Caso de uso"
title: "CU-ver-cuotas-asociado"
description: "Actor: Gestión con permiso para consultar asociados."
tags: [mvp, caso-de-uso]
timestamp: 2026-06-22T00:00:00-03:00
---

# CU-ver-cuotas-asociado

**Actor:** Gestión con permiso para consultar asociados.

**Alcance:** pantalla de lectura que muestra todas las cuotas del asociado seleccionado desde el detalle, sin filtrar por estado.

**Flujo principal:**

1.  El usuario entra al detalle de un asociado.
2.  Selecciona *Ver todas las cuotas*.
3.  El sistema muestra el historial completo de cuotas del asociado, ordenado del período más reciente al más antiguo.
4.  La pantalla conserva el contexto del asociado y muestra la deuda total acumulada.

**Modelos afectados:** Asociado, Cuota, PeríodoCuota.
