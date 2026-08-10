---
type: "Proceso"
title: "Atención, cobranza y administración de cuotas"
description: "Procesos cotidianos de atención y control económico de la mutual."
tags: [mvp, procesos, asociados, cuotas]
timestamp: 2026-08-10T00:00:00-03:00
---

# Atención, cobranza y administración de cuotas

## Atención al asociado y cobranza

**Responsable:** grupo `Atención al asociado`.

**Objetivo:** resolver la consulta cotidiana de una persona, mantener sus datos
ordinarios y registrar cobros o donaciones desde una única ficha.

**Entrada:** identidad del asociado, consulta o importe recibido. **Resultado:**
ficha actualizada, pago distribuido entre cuotas y, si corresponde, donación.

**Recorrido:** buscar asociado → abrir ficha → consultar movimientos → editar o
cobrar → confirmar el resultado en la ficha. Los cobros compuestos conservan un
`operacion_id` común para poder leerlos como una sola operación en auditoría.

**Casos de uso:** [consultar asociados](../casos-de-uso/cu-consultar-asociados.md),
[editar asociado](../casos-de-uso/cu-editar-asociado.md),
[registrar pago](../casos-de-uso/cu-registrar-pago-cuota.md) y
[registrar donación](../casos-de-uso/cu-registrar-donacion.md).

**Controles para capacitación y prueba:** puede consultar, editar y cobrar; no
puede importar, exportar, ver deudores, administrar períodos ni abrir la
auditoría general.

## Administración de cuotas

**Responsable:** grupo `Administrador de la mutual`. `Atención al asociado`
participa en el cobro, pero no administra períodos ni reportes generales.

**Objetivo:** definir períodos, controlar deuda, consultar movimientos y
supervisar la operación regular.

**Entrada:** período de cuota y datos de la operación diaria. **Resultado:**
cuotas generadas y seguimiento disponible. Las importaciones iniciales quedan
fuera de este proceso y están reservadas a `Administrador de la app`.

**Casos de uso:** [generar período](../casos-de-uso/cu-generar-periodo-cuota.md),
[ver cuotas del asociado](../casos-de-uso/cu-ver-cuotas-asociado.md) y
[consultar auditoría](../casos-de-uso/cu-consultar-auditoria.md).

**Controles para capacitación y prueba:** el administrador de la mutual puede
supervisar todos los dominios regulares, pero no ejecuta importaciones masivas,
no administra permisos y no modifica superusuarios.
