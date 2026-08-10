---
type: "Entidad"
title: "Donacion"
description: "Registra un aporte voluntario o el excedente recibido en un cobro."
resource: "cuotas.models.Donacion"
tags: [mvp, modelo-de-datos]
timestamp: 2026-06-22T00:00:00-03:00
---

# Donacion

Registra un aporte voluntario o el excedente recibido en un cobro.

**Campos:**

- id\*
- asociado\*: asociado al que corresponde la donación.
- pago\*: pago que originó el excedente.
- importe\*: importe excedente no aplicado a cuotas.
- fecha\*: fecha del cobro.
- observaciones

**Notas de datos:** queda asociada al pago que la originó. Puede representar el
excedente de un cobro de cuotas o el importe completo de un aporte voluntario
cuando el asociado no tiene deuda; en este último caso, el pago no tiene
aplicaciones `PagoCuota`.

**Referencias funcionales:** ver [reglas de pagos](../reglas/pagos.md),
[registrar pago de cuota](../casos-de-uso/cu-registrar-pago-cuota.md) y
[registrar donación](../casos-de-uso/cu-registrar-donacion.md).
