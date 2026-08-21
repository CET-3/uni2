---
type: "Pantalla"
title: "Asociado"
description: "Asociado"
tags: [mvp, pantalla]
timestamp: 2026-07-13T00:00:00-03:00
---

# Asociado

- La variante de asociado en la home saluda con el nombre y ofrece como CTA `Mi credencial` y `Mis cuotas`. Debajo conserva servicios, beneficios, publicidades y la información para asociarse.
- Mi credencial: encabezado simple y componente institucional `uni2-credential-card` centrado dentro del container responsive de Bootstrap, sin un hero propio.
  La tarjeta usa una franja superior con los cuatro colores fuertes de UNI2,
  reúne una sola vez la identidad y los datos principales, integra el QR y
  comunica la vigencia mediante una banda inferior con color, símbolo y texto.
  El QR contiene la URL absoluta y neutral del entorno. Conserva el UUID
  dentro de un detalle secundario como respaldo, muestra el DNI al titular y explica que el comercio
  necesita conexión. El DNI no se incorpora al QR ni a la copia offline. La
  pantalla muestra el estado calculado `Credencial activa` o `Credencial
  inactiva`, el tipo y el dato institucional —curso o clasificación—. No
  explica la causa de una inactividad ni agrega acciones de cobro: esa
  información pertenece a `Mis cuotas`. La copia offline reutiliza el mismo componente visual,
  conserva el último estado calculado, el tipo y ese dato institucional, pero
  no la causa, DNI, cuotas ni importes.
- Mis cuotas: encabezado simple, resumen con `uni2-metric-card` y tabla responsive dentro de una `uni2-surface-card`; en mobile el total y las métricas se apilan sin perder la tabla ni sus saldos. Cada fila usa un único badge semántico para el estado: verde para `Pagada`, amarillo para `Pendiente` y rojo para `Vencida`; el saldo se mantiene como importe para no duplicar ni contradecir esa señal. Los encabezados y valores monetarios de `Pagado` y `Saldo` se alinean a la derecha para facilitar la comparación vertical.
- Productos y servicios.
- Comercios adheridos.

Las pantallas simples de esta experiencia usan `container py-5` para conservar ancho, margen lateral y separación vertical consistentes en desktop y mobile.
