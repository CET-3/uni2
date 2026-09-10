---
type: "Regla de negocio"
title: "Métricas de administración"
description: "Fuentes, períodos, comparaciones y límites del tablero."
tags: [gestion, metricas, cuotas]
timestamp: 2026-09-10T00:00:00-03:00
---

# Métricas

## METRICAS-001 — Períodos y alcance

Hoy; Esta semana (lunes a hoy); Este mes (1 a hoy); Mes anterior completo;
Este año (1 de enero a hoy); Últimos 12 meses (mes actual y once anteriores,
hasta hoy); Personalizado inclusivo sin fechas futuras. Por defecto Este año,
comparado con el mismo período del año anterior.

Período anterior respeta el avance de semana/mes/año: lunes a jueves se compara
con lunes a jueves de la semana anterior, 1 al 10 con 1 al 10 del mes anterior.
Mes anterior completo compara con otro mes completo, incluso febrero bisiesto.
Personalizado compara con el intervalo inmediatamente anterior de igual duración.
Fechas equivalentes inexistentes se ajustan al último día del mes.

El filtro de padrón (todos/asociados/adherentes) aplica a movimientos, cuotas,
ingresos, solicitudes y deuda. Usa el tipo actualmente conservado; no hay
historial de cambios de tipo. Quiénes somos muestra siempre todo el padrón
activo actual, explícitamente fuera del filtro temporal y de tipo. La oferta
de comercios también es actual e independiente de esos filtros.

## METRICAS-002 — Padrón

Activos al cierre: fecha_alta <= cierre y fecha_baja ausente o > cierre. Una
baja en el día del cierre ya no está activa. Altas y bajas se cuentan por sus
fechas; neto = altas - bajas. No se usa el estado actual para reconstruir el
cierre. Hasta 31 días se muestran puntos diarios; después, cierres mensuales
recortados al rango. Los movimientos se agregan en SQL y se acumulan por punto,
sin recorrer todas las personas ni consultar una vez por punto.

Limitaciones: reimportar padrón puede sobrescribir fecha_alta y conservar una
fecha_baja incompatible con estado activo. No se puede reconstruir historia
perdida. Si se detecta inactivo sin baja, baja anterior al alta o activo con
baja ya efectiva, el total histórico y su serie quedan no disponibles con un
aviso. No se corrigen datos desde el tablero. Las clasificaciones y sus
porcentajes son actuales, no históricos.

## METRICAS-003 — Cuotas y cobranza

Se incluyen las cuotas reales de todos los meses tocados por el rango, aun en
Hoy o Esta semana; no se prorratea una cuota mensual por el número de días.
Generado = suma Cuota.importe (base final almacenada, incluidos prorrateos o
bonificaciones representados en ese importe), no cantidad de personas por
cuota vigente. Se agrupa por año/mes de PeriodoCuota, no por fecha de generación.

Cobrado de esas cuotas = suma por cuota de min(importe base, suma de aplicaciones
PagoCuota hasta hoy). El límite por cuota separa capital de los recargos; las
donaciones están en otra relación. Incluye pagos posteriores al rango e
importados históricos. El pago operativo actual liquida el saldo seleccionado,
no acepta un importe inferior. Las diferencias entre importe_pagado y sus
aplicaciones se informan: las aplicaciones son la fuente de esta métrica.

Cumplimiento = cobrado / generado * 100, sin porcentaje si generado es cero.
Pendiente del período = generado - capital cobrado. Indicador secundario:
personas con todo el capital del período saldado / personas con cuotas del
período. Cuotas de importe cero están saldadas y no crean ingresos.

Ingresos = suma Pago.importe por fecha efectiva dentro del rango; incluye
cuotas anteriores, recargos y donaciones. Excluye importados identificados sin
fecha real confirmada, igual que Atención diaria. Usa todos los operadores,
no la autorización de cobros propios del tablero operativo. Nunca se suma
este valor a cobrado de cuotas: son perspectivas distintas.

Las variaciones muestran diferencia absoluta, flecha y porcentaje sólo con
base anterior positiva. Cumplimiento expresa la diferencia en puntos
porcentuales. Suba favorable verde, baja desfavorable roja y empate neutro,
con texto adicional para no depender del color. Meses antiguos tuvieron más
tiempo para cobrarse; comparar no reconstruye una foto de cobranza pasada.

## METRICAS-004 — Deuda y gestión

Deuda vigente hoy, independiente del período: cuotas con vencimiento < hoy y
saldo positivo calculado con las reglas Cuota.get_saldo_pendiente. Incluye
inactivos con deuda y no depende del estado persistido de la cuota. Se muestra
saldo, recargos, cuotas y personas; grupos 1, 2 y 3+ cuotas vencidas por persona,
y antigüedad de hasta 30 días, 31 a 60 y más de 60 desde vencimiento.

La deuda no se compara como si fuera una foto histórica. El capital pendiente
de las cuotas elegidas y la deuda vencida total de hoy se rotulan por separado.

## METRICAS-005 — Solicitudes y oferta

Solicitudes recibidas por creado_en en el rango (timezone local), agrupadas por
estado actual. Conversión = alta_completada / recibidas. Pendientes = recibida,
observada y datos_aprobados. Una solicitud recibida en agosto y completada en
septiembre pertenece a agosto en este análisis. No confundir esas altas con
todas las altas del padrón; las manuales no provienen de una solicitud.

Oferta: comercios con convenio firmado, agrupados por actividad comercial. El
beneficio está descrito en Comercio.beneficio_texto. No hay métricas de usos,
beneficios consumidos ni series históricas inferidas.

## METRICAS-006 — Permisos y privacidad

gestion.ver_metricas habilita agregados de toda la mutual. Se asigna inicialmente
a Administrador de la mutual, no a Atención al asociado. Los grupos
personalizados pueden recibirlo por el circuito existente.

Listados nominales requieren además consultar_asociados; deuda también
ver_deudores; solicitudes consultar_solicitudes_asociacion. Se validan del lado
servidor, no sólo ocultando enlaces. Pantallas privadas no-store y sin datos
offline. Sin registros de pagos ni modificaciones desde este tablero.
