---
type: "Pantalla"
title: "Asociado"
description: "Asociado"
tags: [mvp, pantalla]
timestamp: 2026-07-13T00:00:00-03:00
---

# Asociado

- La variante de asociado en la home saluda con el nombre y ofrece como CTA `Mi credencial` y `Mis cuotas`. Debajo conserva servicios, beneficios, publicidades y la información para asociarse.
- Mi credencial: presenta directamente el componente institucional
  `uni2-credential-card`, sin hero, kicker, título ni introducción visual que
  repitan el acceso desde la navegación. La tarjeta queda centrada dentro del
  container responsive de Bootstrap.
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
- Mis cuotas: encabezado simple, resumen con `uni2-metric-card` y detalle dentro
  de una `uni2-surface-card`. Las métricas se llaman `Cuotas generadas` y
  `Cuotas con deuda`. En desktop el detalle conserva una tabla y alinea a la
  derecha `Pagado` y `Saldo`; por debajo de `md`, cada cuota pasa a ser una card
  sin desplazamiento horizontal, con período y estado en la cabecera e importes
  en una grilla de dos columnas. Cada registro usa un único badge semántico:
  verde para `Pagada`, amarillo para `Pendiente` y rojo para `Vencida`.
- Mis datos: formulario exclusivo del asociado autenticado con nombre,
  apellido, teléfono, email y dirección. Nombre y apellido son obligatorios;
  los datos de contacto son opcionales. Junto al email se explica que, si queda
  vacío, no estarán disponibles los correos transaccionales ni `Olvidé mi
  contraseña`. La pantalla no muestra ni acepta datos institucionales,
  credenciales, estado o cuotas. Después de guardar presenta los datos
  actualizados y una confirmación.
- Productos y servicios.
- Comercios adheridos.

Las pantallas simples de esta experiencia usan `container py-5` para conservar ancho, margen lateral y separación vertical consistentes en desktop y mobile.
