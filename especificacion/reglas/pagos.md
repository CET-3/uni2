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

## Reintentos y concurrencia

1. Cada formulario de cobro o donación lleva una `clave_operacion` UUID obligatoria,
   generada al abrirlo y conservada ante errores de validación. La base impide
   registrar dos pagos con la misma clave. Un reintento ya registrado informa
   «Esta operación ya fue registrada» o muestra que las cuotas seleccionadas
   ya no son deuda vigente; no genera otro ingreso ni otra donación.
2. Los servicios bloquean la fila del asociado dentro de la transacción antes
   de consultar su deuda. Así dos cobros concurrentes leen la deuda en orden,
   evitando aplicar dos veces un saldo anterior.
3. Dos donaciones deliberadas del mismo importe y fecha son válidas si provienen
   de formularios nuevos, con claves diferentes. No se deduplica por sus montos.
4. Las operaciones internas sin clave generan una al registrar el pago, pero
   deben proporcionar una clave estable si necesitan reconocer sus reintentos.
   Los datos históricos pueden no tener clave. El admin financiero sigue siendo
   de sólo lectura.
