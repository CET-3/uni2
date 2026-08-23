---
type: "Caso de uso"
title: "CU-generar-periodo-cuota"
description: "Actor: Administrador"
tags: [mvp, caso-de-uso]
timestamp: 2026-06-22T00:00:00-03:00
---

# CU-generar-periodo-cuota

**Actor:** Administrador

**Flujo principal:**

1.  Crea `PeríodoCuota` con mes, ciclo lectivo, importe y vencimiento. El vencimiento debe pertenecer al mismo mes y año del período seleccionado.
2.  Ejecuta generación de cuotas.
3.  El sistema genera para asociados activos alcanzados por `fecha_inicio_cobro`.
4.  El sistema registra en `generado_el` la fecha y hora de esta primera
    ejecución, incluso si genera cero cuotas, y audita la transición con el
    mismo actor y operación.
5.  Evita duplicados. Si la generación se reejecuta, conserva la primera fecha.

**Reglas relacionadas:** [Asociados](../reglas/asociados.md), [Cuotas](../reglas/cuotas.md).

**Situaciones especiales:** ciclo lectivo inexistente, vencimiento fuera del
período seleccionado, asociado inactivo, `fecha_inicio_cobro` posterior, cuota
ya generada y ejecución sin asociados elegibles.

**Modelos afectados:** CicloLectivo, PeríodoCuota, Cuota, Asociado.
