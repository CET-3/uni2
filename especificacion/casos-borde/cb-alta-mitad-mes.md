---
type: "Caso borde"
title: "CB-alta-mitad-mes"
description: "Situación: el alta ocurre cerca del cierre del período mensual."
tags: [mvp, caso-borde]
timestamp: 2026-06-22T00:00:00-03:00
---

# CB-alta-mitad-mes

**Situación:** el alta ocurre cerca del cierre del período mensual.

**Respuesta esperada:** si ocurre antes del día 15, paga el mes actual; si ocurre después del día 15, comienza a pagar desde el mes siguiente. El administrador puede ajustar `fecha_inicio_cobro`.

**Caso de uso relacionado:** [CU-crear-asociado](../casos-de-uso/cu-crear-asociado.md).

**Relacionado con:** [ALTA-ASOCIADO-001](../reglas/altas-de-asociado.md#alta-asociado-001), [ALTA-ASOCIADO-002](../reglas/altas-de-asociado.md#alta-asociado-002), [ALTA-ASOCIADO-003](../reglas/altas-de-asociado.md#alta-asociado-003).
