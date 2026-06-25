---
type: "Regla de negocio"
title: "Altas de asociado"
description: "Reglas de negocio sobre altas de asociado."
tags: [mvp, reglas]
timestamp: 2026-06-22T00:00:00-03:00
---

# Altas de asociado

## ALTA-ASOCIADO-001

Si el alta ocurre antes del día 15, el asociado paga el mes actual.

## ALTA-ASOCIADO-002

Si el alta ocurre después del día 15, comienza a pagar desde el mes siguiente.

## ALTA-ASOCIADO-003

La fecha de alta y la fecha de inicio de cobro son independientes. El sistema debe usar `fecha_inicio_cobro` para generar cuotas.

## ALTA-ASOCIADO-004

Al crear un asociado, el sistema genera cuotas para los 2 meses anteriores al mes de alta y el mes actual, siempre que existan períodos de cuota activos para esos meses.

## ALTA-ASOCIADO-005

El alta de asociado no crea períodos de cuota automáticamente. Si faltan períodos para alguno de los 3 meses, no se genera la cuota correspondiente. La administración debe crear los períodos desde la pantalla de períodos de cuota.
