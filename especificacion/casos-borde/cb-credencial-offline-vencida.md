---
type: "Caso borde"
title: "CB-credencial-offline-vencida"
description: "Situación: la copia local de la credencial tiene más de siete días."
tags: [pwa, caso-borde, credencial, offline]
timestamp: 2026-08-01T00:00:00-03:00
---

# CB-credencial-offline-vencida

**Situación:** El asociado abre Mi credencial sin conexión y la copia fue
actualizada hace más de siete días.

**Comportamiento esperado:**

- Uni2 no muestra nombre, token ni datos de la copia vencida.
- El registro vencido se elimina del almacenamiento privado.
- Se informa que debe conectarse y abrir nuevamente la credencial.
- No se amplía el plazo usando sólo la hora local sin una carga correcta desde
  el servidor.
