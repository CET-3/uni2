---
type: "Caso borde"
title: "CB-enlace-solicitud-invalido"
description: "Situación: el enlace privado no existe, venció o fue reemplazado."
tags: [post-mvp, caso-borde, diseno-aprobado]
timestamp: 2026-08-26T00:00:00-03:00
---

# CB-enlace-solicitud-invalido

**Situación:** la persona abre un token inexistente, vencido o invalidado por
una emisión posterior.

**Respuesta esperada:** la pantalla no confirma si existe una solicitud ni
muestra datos personales. Informa que el enlace no está disponible y ofrece
los datos de contacto de la Mutual. Un operador autorizado puede emitir un
enlace nuevo sin cambiar el estado.

**Caso de uso relacionado:** [CU-preinscribirse-asociacion](../casos-de-uso/cu-preinscribirse-asociacion.md).

**Relacionado con:** [SOLICITUD-ASOCIACION-007](../reglas/solicitudes-asociacion.md#solicitud-asociacion-007--enlace-privado).
