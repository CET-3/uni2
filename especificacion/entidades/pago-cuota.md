---
type: "Entidad"
title: "PagoCuota"
description: "Aplicación de un pago a una cuota."
resource: "cuotas.models.PagoCuota"
tags: [mvp, modelo-de-datos]
timestamp: 2026-06-22T00:00:00-03:00
---

# PagoCuota

Aplicación de un pago a una cuota.

**Campos:**

- id\*
- pago\*
- cuota\*
- importe\*

**Notas de datos:** permite saber qué cuotas fueron cubiertas por cada pago. Un pago puede aplicarse a varias cuotas mediante varios registros `PagoCuota`.

**Referencias funcionales:** ver [reglas de pagos](../reglas/pagos.md) y [registrar pago de cuota](../casos-de-uso/cu-registrar-pago-cuota.md).

**Ejemplo:** pago de \$6000 distribuido entre cuota marzo \$3000 y cuota abril \$3000.
