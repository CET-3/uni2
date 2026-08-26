---
type: "Caso borde"
title: "CB-solicitud-asociacion-duplicada"
description: "Situación: el DNI ya pertenece a un asociado o a otra solicitud abierta."
tags: [post-mvp, caso-borde, diseno-aprobado]
timestamp: 2026-08-26T00:00:00-03:00
---

# CB-solicitud-asociacion-duplicada

**Situación:** se intenta enviar una preinscripción cuyo DNI normalizado ya
pertenece a un asociado o a una solicitud no cancelada.

**Respuesta esperada:** no se crea otra solicitud. La respuesta pública es
neutra, no revela datos ni estado de la persona existente y explica cómo
contactar a la Mutual. Una solicitud cancelada sí permite una presentación nueva.

**Caso de uso relacionado:** [CU-preinscribirse-asociacion](../casos-de-uso/cu-preinscribirse-asociacion.md).

**Relacionado con:** [SOLICITUD-ASOCIACION-004](../reglas/solicitudes-asociacion.md#solicitud-asociacion-004--duplicados).
