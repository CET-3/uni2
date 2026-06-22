---
type: "Entidad"
title: "Cuota"
description: "Representa una cuota concreta de un asociado para un período."
resource: "cuotas.models.Cuota"
tags: [mvp, modelo-de-datos]
timestamp: 2026-06-22T00:00:00-03:00
---

# Cuota

Representa una cuota concreta de un asociado para un período.

**Campos:**

- id\*
- asociado\*
- período\*
- importe\*
- importe_recargo_mes\*: recargo que aplica si se paga en el mismo mes después del vencimiento (copia del período).
- importe_recargo_mes_siguiente\*: recargo que aplica si se paga en un mes posterior al vencimiento (copia del período).
- importe_pagado\*
- estado\*: estado administrativo persistido.
- fecha_generación\*

**Estados persistidos:** pendiente, pagada, vencida.

**Restricción:** no puede existir más de una cuota para el mismo asociado y período.

**Notas de datos:** guarda su propio importe y sus propios importes de recargo para conservar historial aunque cambie el período. El saldo exigible, el recargo aplicable y el estado mostrado en pantallas se calculan para una fecha de referencia.

**Referencias funcionales:** ver [reglas de cuotas](../reglas/cuotas.md), [reglas de pagos](../reglas/pagos.md) y [registrar pago de cuota](../casos-de-uso/cu-registrar-pago-cuota.md).
