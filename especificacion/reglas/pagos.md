---
type: "Regla de negocio"
title: "Pagos"
description: "Reglas de negocio sobre pagos."
tags: [mvp, reglas]
timestamp: 2026-06-22T00:00:00-03:00
---

# Pagos

## Selección de cuotas

1. La persona de gestión selecciona una o más cuotas para cobrar. La selección debe empezar desde la cuota pendiente más antigua; no se puede cobrar una cuota más nueva dejando una anterior sin pagar.
2. No se permiten pagos parciales de cuotas. Cada cuota incluida en un cobro debe quedar totalmente cancelada.
3. Si el pago se registra después del vencimiento, el importe exigible incluye el recargo que corresponda según las [reglas de cuotas](cuotas.md).

## Registro del pago

1. Un cobro puede incluir varias cuotas. El pago se registra como un único `Pago` y cada cuota cobrada genera un `PagoCuota` asociado.
2. `Pago.importe` representa el total recibido. Los `PagoCuota` explican cómo se distribuye ese importe entre las cuotas.
3. El importe recibido no puede ser menor que el total exigible de las cuotas incluidas.
4. Si el importe recibido supera el total exigible, el excedente se registra como donación. El MVP no maneja saldo a favor.
5. Los métodos de pago permitidos en el MVP son efectivo y billetera virtual.

## Donación sin deuda

1. Si el asociado no tiene cuotas pendientes, gestión puede registrar un aporte voluntario desde su detalle.
2. El sistema crea un `Pago` sin aplicaciones `PagoCuota` y una `Donacion` por el importe total recibido.
3. Si existen cuotas pendientes, no se permite una donación aislada: primero deben incluirse las cuotas más antiguas y solo el excedente se registra como donación.
4. La donación debe ser mayor que cero y no genera saldo a favor.
