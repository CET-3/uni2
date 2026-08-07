---
type: "Caso borde"
title: "CB-operacion-sin-conexion"
description: "Situación: se intenta enviar un formulario mientras no hay red."
tags: [pwa, caso-borde, offline, formularios]
timestamp: 2026-08-01T00:00:00-03:00
---

# CB-operacion-sin-conexion

**Situación:** Una persona intenta cobrar, validar una credencial, iniciar o
cerrar sesión, guardar un cambio o subir un archivo sin conexión.

**Comportamiento esperado:**

- Se realiza como máximo un intento contra el servidor.
- La operación no se guarda localmente.
- No se reenvía automáticamente al recuperar conexión.
- Se informa claramente que no fue enviada ni quedó pendiente.
- La persona debe revisar la conexión y repetir la acción conscientemente.

**Motivo:** Evitar duplicaciones y cambios aplicados fuera del contexto en el
que fueron confirmados.
