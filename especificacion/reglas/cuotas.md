---
type: "Regla de negocio"
title: "Cuotas"
description: "Reglas de negocio sobre cuotas."
tags: [mvp, reglas]
timestamp: 2026-06-22T00:00:00-03:00
---

# Cuotas

## Características de la cuota

1. No puede existir más de una cuota por asociado y período.
2. Cada cuota almacena su propio importe.
3. La cuota tiene un atributo `estado` que se almacena. Se crea con estado `Pendiente` y pasa a `Pagada` cuando se registra el cobro completo.
4. El recargo sobre una cuota tiene dos niveles, ambos definidos en `PeriodoCuota`:
   - **Recargo por vencimiento:** se aplica si el pago se realiza después del día 10 del mes del período.
   - **Recargo por mora:** se aplica si la cuota no se saldó durante el mes del período. Se suma al recargo por vencimiento.
5. El estado `Vencida` no se almacena: se determina en el momento de mostrar la cuota, comparando la fecha de vencimiento con una fecha de referencia explícita. Las pantallas siempre calculan el estado y el saldo para una fecha de referencia.

## Exigibilidad para la credencial

El estado de la credencial usa un corte fijo independiente del cálculo de
recargos y de `PeriodoCuota.fecha_vencimiento`:

1. Una cuota impaga de un mes anterior inactiva la credencial.
2. La cuota del mes actual no la inactiva hasta el día 10 inclusive; desde el
   día 11 la inactiva si conserva cualquier saldo, incluso parcial.
3. Las cuotas de períodos futuros no afectan la credencial.
4. Las cuotas de períodos futuros no forman parte de la deuda exigible y no se
   pueden cobrar antes de que comience su mes.
5. Una cuota exigible totalmente pagada no la inactiva.

## Creación de cuotas

Cada mes, el administrador del sistema crea el próximo período de cuota desde la sección Períodos de cuota. Al crearlo define la fecha, la fecha de vencimiento, el importe y el recargo por mora. Una vez creado el período, ejecuta la operación de generar cuotas, que crea una cuota por cada asociado activo elegible.

1. Si la cuota ya existe para el asociado y período, no debe generarse otra.
2. Los dos valores de recargo (por vencimiento y por mora) deben copiarse desde `PeriodoCuota` a `Cuota` al momento de generarla.
3. Al crear un nuevo asociado, se generan automáticamente las cuotas que le corresponden según las [reglas de alta de asociado](altas-de-asociado.md).
4. La fecha de vencimiento debe estar dentro del mismo mes y año definidos por `PeriodoCuota.mes` y su ciclo lectivo. No se admiten fechas de meses anteriores ni posteriores.
5. La primera ejecución de la generación masiva completa
   `PeriodoCuota.generado_el`, aunque no encuentre asociados elegibles y genere
   cero cuotas. La ejecución y la transición del campo quedan agrupadas en la
   misma operación de auditoría.
6. Reejecutar la generación conserva el valor original de `generado_el`, no
   duplica cuotas y no genera un segundo evento por ese campo.
7. Durante la migración inicial del marcador, los períodos históricos que ya
   tienen al menos una cuota reciben la fecha de la migración. No es posible
   inferir si un período histórico sin cuotas fue generado con resultado cero,
   por lo que esos períodos permanecen sin marca.
8. La generación masiva y la generación inicial de un alta bloquean los
   períodos mientras deciden y crean cuotas. Los bloqueos se toman en orden
   cronológico para que, si ambas operaciones coinciden, el alta vea la marca
   de generación o la generación masiva vea al nuevo asociado; ninguna de las
   dos puede dejar la cuota omitida por una lectura intermedia.

## Borrado excepcional de períodos

Durante la depuración excepcional de la carga inicial, un superusuario puede
eliminar períodos de cuota desde el admin técnico, tanto individualmente como
con la acción masiva de Django. Un período que todavía tenga cuotas relacionadas
no se puede eliminar: `Cuota.periodo` conserva la protección `PROTECT` y la
limpieza debe eliminar primero los asociados y sus cuotas.

Esta excepción no habilita el borrado directo de `Cuota`, `Pago`, `PagoCuota` o
`Donacion`.

## Importe publicado

La cuota social informada en el sitio público toma el importe del
`PeriodoCuota` correspondiente al mes y año actuales. El campo `activo` no se
usa para esta consulta porque controla la generación de cuotas, no la vigencia
informativa del importe.

Si no existe un período para el mes actual —por ejemplo durante vacaciones— se
usa el período cronológicamente anterior más reciente. Si todavía no hay un
período anterior pero existe alguno configurado, se usa el último disponible.
Si no existe ningún período, la interfaz invita a consultar el valor vigente y
nunca muestra un importe fijo.
