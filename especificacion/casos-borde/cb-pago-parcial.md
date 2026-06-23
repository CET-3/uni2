---
type: "Caso borde"
title: "CB-pago-parcial"
description: "Situación: el importe ingresado no alcanza para cancelar una cuota completa."
tags: [mvp, caso-borde]
timestamp: 2026-06-22T00:00:00-03:00
---

# CB-pago-parcial

**Situación:** el importe recibido no alcanza para cancelar todas las cuotas incluidas en el cobro.

**Respuesta esperada:** el sistema rechaza la operación. En el MVP no se registran pagos parciales de cuota desde la pantalla de cobro.

**Caso de uso relacionado:** [CU-registrar-pago-cuota](../casos-de-uso/cu-registrar-pago-cuota.md).

**Relacionado con:** [PAGO-002](../reglas/pagos.md#pago-002), [PAGO-007](../reglas/pagos.md#pago-007).
