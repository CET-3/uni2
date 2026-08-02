---
type: "Caso borde"
title: "CB-actualizacion-PWA-con-formulario-abierto"
description: "Situación: hay una versión nueva mientras una persona completa un formulario."
tags: [pwa, caso-borde, actualizacion]
timestamp: 2026-08-01T00:00:00-03:00
---

# CB-actualizacion-PWA-con-formulario-abierto

**Situación:** El navegador descarga una versión nueva mientras una persona
está escribiendo o revisando un formulario.

**Comportamiento esperado:**

- La versión nueva queda esperando.
- Uni2 avisa que existe una actualización, sin recargar.
- La persona puede terminar o cancelar su trabajo antes de actualizar.
- Al aceptar, se activa la versión nueva y se recarga una sola vez.
- Los cachés PWA de versiones anteriores se eliminan al activar.
