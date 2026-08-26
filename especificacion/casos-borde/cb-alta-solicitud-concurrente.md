---
type: "Caso borde"
title: "CB-alta-solicitud-concurrente"
description: "Situación: dos operadores intentan completar o cambiar la misma solicitud."
tags: [post-mvp, caso-borde, diseno-aprobado]
timestamp: 2026-08-26T00:00:00-03:00
---

# CB-alta-solicitud-concurrente

**Situación:** dos operadores actúan sobre la misma solicitud o el DNI se
incorpora al padrón mediante otro flujo antes de completar el alta.

**Respuesta esperada:** el sistema vuelve a comprobar estado y duplicados
dentro de la transacción. Solo una operación puede crear el asociado; la otra
se rechaza, no genera cuotas ni correos duplicados y muestra la ficha actualizada.

**Caso de uso relacionado:** [CU-gestionar-solicitud-asociacion](../casos-de-uso/cu-gestionar-solicitud-asociacion.md).

**Relacionado con:** [SOLICITUD-ASOCIACION-009](../reglas/solicitudes-asociacion.md#solicitud-asociacion-009--alta-presencial).
