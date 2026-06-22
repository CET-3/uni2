---
type: "Caso borde"
title: "CB-pago-mayor-a-minimo-calculado"
description: "Situación: se registra un importe recibido mayor que el mínimo calculado para las cuotas incluidas."
tags: [mvp, caso-borde]
timestamp: 2026-06-22T00:00:00-03:00
---

# CB-pago-mayor-a-minimo-calculado

**Situación:** se registra un importe recibido mayor que el mínimo calculado para las cuotas incluidas.

**Respuesta esperada:** el sistema registra el pago de las cuotas incluidas y registra el excedente como `Donacion`. No genera saldo a favor.

**Caso de uso relacionado:** [CU-registrar-pago-cuota](/casos-de-uso/cu-registrar-pago-cuota.md).

**Relacionado con:** [PAGO-008](/reglas/pagos.md#pago-008).
