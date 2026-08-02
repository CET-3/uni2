---
type: "Caso borde"
title: "CB-cambio-usuario-en-dispositivo"
description: "Situación: otra persona inicia sesión en un dispositivo con una credencial guardada."
tags: [pwa, caso-borde, privacidad, credencial]
timestamp: 2026-08-01T00:00:00-03:00
---

# CB-cambio-usuario-en-dispositivo

**Situación:** El asociado A guardó su credencial y luego se autentica el
asociado B en el mismo navegador.

**Comportamiento esperado:**

- El cierre de sesión de A intenta eliminar inmediatamente la copia.
- Al reconocer la identidad de B, Uni2 realiza una segunda comprobación
  defensiva.
- Si la copia no pertenece a B, se elimina antes de representar datos.
- B nunca ve nombre, número ni token de A.
- Si B desea su propia copia, debe aceptar guardarla.

Esta doble protección cubre también un cierre abrupto o una limpieza cliente
incompleta.
