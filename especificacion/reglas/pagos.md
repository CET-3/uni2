---
type: "Regla de negocio"
title: "Pagos"
description: "Reglas de negocio sobre pagos."
tags: [mvp, reglas]
timestamp: 2026-06-22T00:00:00-03:00
---

# Pagos

## PAGO-001

Los pagos se aplican a la deuda más antigua primero.

## PAGO-002

No se permiten pagos parciales de cuotas desde el cobro de gestión del MVP. Cada cuota incluida en un cobro debe quedar totalmente pagada.

## PAGO-003

La persona de gestión selecciona una o más cuotas para cobrar. La selección debe ser continua desde la cuota pendiente más vieja; no se puede cobrar una cuota más nueva dejando una anterior pendiente.

## PAGO-004

Si el pago se registra después del vencimiento y la cuota no estaba cancelada, la deuda exigible incluye el recargo fijo por mora.

## PAGO-005

Un pago puede aplicarse a varias cuotas mediante PagoCuota.

## PAGO-006

Los métodos permitidos en MVP son efectivo y billetera_virtual.

## PAGO-007

El importe recibido no puede ser menor que el total exigible de las cuotas incluidas en el cobro.

## PAGO-008

Si el importe recibido supera el total exigible de las cuotas incluidas, el excedente se registra como donación. El MVP no maneja saldo a favor.

## PAGO-009

`Pago.importe` representa el total recibido en la operación de cobro. El destino de ese dinero se explica mediante sus aplicaciones: `PagoCuota` para cuotas, `Donacion` para excedentes voluntarios y, en V2, `PagoPedido` para pedidos.
