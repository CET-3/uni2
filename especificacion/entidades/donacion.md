---
type: "Entidad"
title: "Donacion"
description: "Registra el excedente voluntario recibido en un cobro."
resource: "cuotas.models.Donacion"
tags: [mvp, modelo-de-datos]
timestamp: 2026-06-22T00:00:00-03:00
---

# Donacion

Registra el excedente voluntario recibido en un cobro.

**Campos:**

- id\*
- asociado\*: asociado al que corresponde la donación.
- pago\*: pago que originó el excedente.
- importe\*: importe excedente no aplicado a cuotas.
- fecha\*: fecha del cobro.
- observaciones

**Notas de datos:** queda asociada al pago que originó el excedente.

**Referencias funcionales:** ver [reglas de pagos](../reglas/pagos.md) y [registrar pago de cuota](../casos-de-uso/cu-registrar-pago-cuota.md).
