---
type: "Regla de negocio"
title: "Cuotas"
description: "Reglas de negocio sobre cuotas."
tags: [mvp, reglas]
timestamp: 2026-06-22T00:00:00-03:00
---

# Cuotas

## CUOTA-001

No puede existir más de una cuota por asociado y período.

## CUOTA-002

Cada cuota almacena su propio importe.

## CUOTA-003

Una cuota puede mostrarse como pendiente, pagada o vencida. Ese estado operativo se calcula para una fecha de referencia junto con el recargo aplicable y el saldo exigible.

## CUOTA-004

Se generan cuotas para asociados activos cuya fecha_inicio_cobro sea menor o igual al período generado.

## CUOTA-005

Si la cuota ya existe para el asociado y período, no debe generarse otra.

## CUOTA-006

Si al vencimiento la cuota no esta totalmente cancelada, se aplica un recargo fijo por mora una sola vez.

## CUOTA-007

El recargo por mora debe copiarse desde `PeríodoCuota` a `Cuota` al momento de generarla.

## CUOTA-008

Una cuota no "sabe" sola si está vencida: está vencida mirando una fecha. Las pantallas deben mostrar estado y saldo calculados para una fecha de referencia explícita.
