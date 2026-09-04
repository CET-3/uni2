---
type: "Regla de negocio"
title: "Altas de asociado"
description: "Reglas de negocio sobre altas de asociado."
tags: [mvp, reglas]
timestamp: 2026-06-22T00:00:00-03:00
---

# Altas de asociado

## ALTA-ASOCIADO-001

Si el tipo es `Asociado`, `fecha_inicio_cobro` es el primer día del mes
correspondiente a dos meses antes de `fecha_alta`. La regla no depende del día
del mes en que ocurre el alta.

## ALTA-ASOCIADO-002

Si el tipo es `Adherente`, `fecha_inicio_cobro` es el primer día del mismo mes
de `fecha_alta`. La regla no depende del día del mes en que ocurre el alta.

## ALTA-ASOCIADO-003

La fecha de alta y la fecha de inicio de cobro son datos independientes. El
sistema usa `fecha_inicio_cobro` como límite inferior único para generar
cuotas. Una fecha explícita proveniente de una importación o corrección
administrativa tiene prioridad sobre el cálculo automático.

## ALTA-ASOCIADO-004

Al realizar un alta manual, el sistema genera cuotas para los períodos activos
existentes desde `fecha_inicio_cobro` hasta el mes de alta. También incorpora
los períodos futuros activos cuya generación masiva ya se ejecutó, identificados
por `PeriodoCuota.generado_el`.

## ALTA-ASOCIADO-005

El alta no crea períodos de cuota automáticamente. Si falta un período o está
inactivo, no se genera la cuota correspondiente. Un período futuro creado pero
todavía no generado tampoco se incorpora al alta.

## ALTA-ASOCIADO-006

En el alta manual cotidiana, la fecha de alta es la fecha local del sistema y
no se puede editar. La fecha de inicio de cobro tampoco se solicita: se calcula
automáticamente con las reglas `ALTA-ASOCIADO-001` y `ALTA-ASOCIADO-002`. Ambas
fechas continúan editables en la edición administrativa y en el admin técnico.

## ALTA-ASOCIADO-007

Los registros existentes no se recalculan al incorporar esta regla. Cambiar el
tipo durante una edición tampoco modifica automáticamente
`fecha_inicio_cobro`; cualquier corrección posterior debe ser explícita y queda
auditada.
