---
type: "Pantalla"
title: "Asociado"
description: "Asociado"
tags: [mvp, pantalla]
timestamp: 2026-07-13T00:00:00-03:00
---

# Asociado

- La variante de asociado en la home saluda con el nombre y ofrece como CTA `Mi credencial` y `Mis cuotas`. Debajo conserva servicios, beneficios, publicidades y la información para asociarse.
- Mi credencial: encabezado simple y componente `uni2-credential` centrado dentro del container responsive de Bootstrap, sin un hero propio.
  El QR contiene la URL absoluta y neutral del entorno. Conserva el UUID
  visible como respaldo, muestra el DNI al titular y explica que el comercio
  necesita conexión. El DNI no se incorpora al QR ni a la copia offline.
- Mis cuotas: encabezado simple, resumen con `uni2-metric-card` y tabla responsive dentro de una `uni2-surface-card`; en mobile el total y las métricas se apilan sin perder la tabla ni sus saldos.
- Productos y servicios.
- Comercios adheridos.

Las pantallas simples de esta experiencia usan `container py-5` para conservar ancho, margen lateral y separación vertical consistentes en desktop y mobile.
