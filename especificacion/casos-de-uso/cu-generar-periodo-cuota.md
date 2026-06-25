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

1.  Crea `PeríodoCuota` con mes, ciclo lectivo, importe y vencimiento.
2.  Ejecuta generación de cuotas.
3.  El sistema genera para asociados activos alcanzados por `fecha_inicio_cobro`.
4.  Evita duplicados.

**Reglas relacionadas:** [Asociados](../reglas/asociados.md), [Cuotas](../reglas/cuotas.md).

**Situaciones especiales:** ciclo lectivo inexistente, asociado inactivo, fecha_inicio_cobro posterior, cuota ya generada.

**Modelos afectados:** CicloLectivo, PeríodoCuota, Cuota, Asociado.
