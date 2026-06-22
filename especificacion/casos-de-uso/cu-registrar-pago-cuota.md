---
type: "Caso de uso"
title: "CU-registrar-pago-cuota"
description: "Actor: Administrador"
tags: [mvp, caso-de-uso]
timestamp: 2026-06-22T00:00:00-03:00
---

# CU-registrar-pago-cuota

**Actor:** Gestión con permiso para cobrar cuotas.

**Alcance:** el cobro no tiene búsqueda propia de asociados. La búsqueda se realiza en [CU-consultar-asociados](/casos-de-uso/cu-consultar-asociados.md) y desde allí se accede a registrar el pago del asociado seleccionado.

**Flujo principal:**

1.  Busca el asociado desde la consulta operativa de asociados.
2.  Selecciona la acción de cobrar.
3.  El sistema muestra las cuotas pendientes del asociado, ordenadas de la más vieja a la más nueva.
4.  Para cada cuota pendiente, el sistema muestra período, importe original, recargo aplicable a la fecha de cobro, total exigible actual, importe pagado, saldo a cubrir y estado.
5.  La persona de gestión selecciona una o más cuotas para cobrar.
6.  El sistema valida que la selección sea continua desde la cuota pendiente más vieja. No se puede seleccionar una cuota más nueva dejando una anterior pendiente.
7.  El sistema calcula el importe mínimo a cobrar como la suma de los saldos exigibles seleccionados.
8.  El campo de importe recibido se prellena con ese mínimo.
9.  La persona de gestión confirma fecha, método e importe recibido. El importe recibido puede ser igual o mayor al mínimo calculado.
10. El sistema crea un `Pago` con el importe total recibido.
11. El sistema aplica el pago a las cuotas seleccionadas, siempre de la deuda más antigua a la más nueva.
12. Actualiza las cuotas seleccionadas como pagadas.
13. Crea `PagoCuota` por cada cuota cubierta.
14. Si el importe recibido supera el mínimo calculado, registra el excedente como `Donacion`.

**Reglas relacionadas:** [PAGO-001](/reglas/pagos.md#pago-001), [PAGO-002](/reglas/pagos.md#pago-002), [PAGO-003](/reglas/pagos.md#pago-003), [PAGO-004](/reglas/pagos.md#pago-004), [PAGO-005](/reglas/pagos.md#pago-005), [PAGO-006](/reglas/pagos.md#pago-006), [PAGO-007](/reglas/pagos.md#pago-007), [PAGO-008](/reglas/pagos.md#pago-008), [PAGO-009](/reglas/pagos.md#pago-009).

**Situaciones especiales:** pago exacto, pago de una cuota, pago de varias cuotas, pago mayor al mínimo calculado, importe recibido menor al mínimo calculado, asociado sin deuda.

**Modelos afectados:** Pago, PagoCuota, Cuota, Donacion.
