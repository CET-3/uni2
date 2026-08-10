---
type: "Caso borde"
title: "CB-qr-invalido"
description: "Situación: el token del QR no existe o es inválido."
tags: [mvp, caso-borde]
timestamp: 2026-06-22T00:00:00-03:00
---

# CB-qr-invalido

**Situación:** el token del QR no existe o es inválido.

**Respuesta esperada:** el sistema muestra una respuesta genérica sin nombre,
estado ni confirmación de que el token pertenece a una cuenta. Un formato que
no sea UUID responde como recurso no encontrado.

**Caso de uso relacionado:** [CU-validar-credencial](../casos-de-uso/cu-validar-credencial.md).

**Relacionado con:** [CREDENCIAL-003](../reglas/credenciales.md#credencial-003).
