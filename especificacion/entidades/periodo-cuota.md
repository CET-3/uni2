---
type: "Entidad"
title: "PeríodoCuota"
description: "Representa un período mensual de cuota."
resource: "cuotas.models.PeriodoCuota"
tags: [mvp, modelo-de-datos]
timestamp: 2026-06-22T00:00:00-03:00
---

# PeríodoCuota

Representa un período mensual de cuota.

**Campos:**

- id\*: identificador interno del período.
- mes\*: mes del período (1 a 12).
- ciclo_lectivo\*: año lectivo al que corresponde este período. FK a CicloLectivo.
- importe\*: importe base de la cuota para este período.
- importe_recargo_mes\*: recargo fijo que se suma si se paga después del vencimiento pero dentro del mismo mes.
- importe_recargo_mes_siguiente\*: recargo fijo que se suma si se paga en un mes posterior al vencimiento.
- fecha_vencimiento\*: fecha límite para pagar sin recargo.
- activo\*: indica si este período está activo para generar cuotas.

**Notas de datos:** define importe base, vencimiento y dos importes de recargo por mora. Esos importes sirven como fuente para las cuotas generadas.

**Referencias funcionales:** ver [reglas de cuotas](../reglas/cuotas.md), [reglas de pagos](../reglas/pagos.md) y [generar período de cuota](../casos-de-uso/cu-generar-periodo-cuota.md).

**Ejemplo:** Mayo 2026 - \$800 - recargo mismo mes \$100 - recargo mes siguiente \$200 - vence 10/05/2026.
