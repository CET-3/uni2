---
type: "Caso de uso"
title: "CU-registrar-donacion"
description: "Actor: Gestión con permiso para cobrar cuotas."
tags: [mvp, caso-de-uso]
timestamp: 2026-08-10T00:00:00-03:00
---

# CU-registrar-donacion

**Actor:** Gestión con permiso `gestion.cobrar_cuotas`.

**Precondición:** el asociado no tiene cuotas pendientes.

**Flujo principal:**

1. Busca al asociado desde `Atención al asociado` y abre su detalle.
2. Como la deuda es cero, la acción principal se presenta como `Registrar donación`.
3. El sistema informa que el importe ingresado se registrará íntegramente como donación.
4. La persona de gestión completa fecha, importe, método y, si corresponde, observaciones.
5. El sistema crea un `Pago` por el total recibido, sin aplicaciones `PagoCuota`.
6. El sistema crea una `Donacion` por el mismo importe y la vincula al pago y al asociado.
7. La operación queda registrada en auditoría como `Registro de donación`.
8. El sistema confirma la operación y vuelve al detalle del asociado.

**Reglas:** el importe debe ser mayor que cero. Si el asociado tiene cuotas
pendientes, este recorrido no está disponible: primero se debe usar el cobro de
cuotas y cualquier excedente puede registrarse como donación. La donación no
genera saldo a favor.

**Cancelación y errores:** `Cancelar` vuelve al detalle sin registrar cambios.
Un formulario inválido conserva los datos ingresados. Si aparece deuda antes de
confirmar, la operación se rechaza sin crear el pago ni la donación.

**Modelos afectados:** Pago, Donacion.

**Referencias:** [reglas de pagos](../reglas/pagos.md),
[Donacion](../entidades/donacion.md) y
[registrar pago de cuota](cu-registrar-pago-cuota.md).
