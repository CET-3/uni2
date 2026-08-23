---
type: "Caso borde"
title: "CB-alta-mitad-mes"
description: "Situación: el alta ocurre cerca del cierre del período mensual."
tags: [mvp, caso-borde]
timestamp: 2026-06-22T00:00:00-03:00
---

# CB-alta-mitad-mes

**Situación:** el alta ocurre cerca del cierre del período mensual.

**Respuesta esperada:** el día del alta no cambia el cálculo. Un `Asociado`
comienza dos meses antes y un `Adherente` comienza en el mes actual. Si la
administración ya ejecutó la generación de un período futuro, el alta también
recibe esa cuota; si el período sólo fue creado, no la recibe. El administrador
puede ajustar `fecha_inicio_cobro` de manera explícita.

**Caso de uso relacionado:** [CU-crear-asociado](../casos-de-uso/cu-crear-asociado.md).

**Relacionado con:** [ALTA-ASOCIADO-001](../reglas/altas-de-asociado.md#alta-asociado-001), [ALTA-ASOCIADO-002](../reglas/altas-de-asociado.md#alta-asociado-002), [ALTA-ASOCIADO-003](../reglas/altas-de-asociado.md#alta-asociado-003).
