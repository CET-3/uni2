---
type: "Entidad"
title: "Pago"
description: "Representa un ingreso de dinero."
resource: "cuotas.models.Pago"
tags: [mvp, modelo-de-datos]
timestamp: 2026-06-22T00:00:00-03:00
---

# Pago

Representa un ingreso de dinero.

**Campos:**

- id\*
- asociado\*
- fecha\*
- importe\*: importe total recibido en la operación de cobro.
- método\*
- observaciones
- registrado_por
- clave_operacion: UUID único que identifica el envío de cobro y evita duplicados.
  Obligatorio en el formulario de gestión; generado por el servicio para llamadas
  internas sin clave. NULL permitido para pagos históricos. No editable en el admin.

**Métodos:** efectivo, billetera_virtual.

**Notas de datos:** representa la cabecera de una operación de cobro. En el MVP puede tener aplicaciones a cuotas mediante `PagoCuota` y un excedente mediante `Donacion`. En V2 podrá aplicarse también a pedidos mediante PagoPedido.

**Referencias funcionales:** ver [reglas de pagos](../reglas/pagos.md), [registrar pago de cuota](../casos-de-uso/cu-registrar-pago-cuota.md) y [Donacion](donacion.md).
