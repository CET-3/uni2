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

## Creación de cuotas

Cada mes, el administrador del sistema crea el próximo período de cuota desde la sección Períodos de cuota. Al crearlo define la fecha, la fecha de vencimiento, el importe y el recargo por mora. Una vez creado el período, ejecuta la operación de generar cuotas, que crea una cuota por cada asociado activo elegible.

1. Si la cuota ya existe para el asociado y período, no debe generarse otra.
2. Los dos valores de recargo (por vencimiento y por mora) deben copiarse desde `PeriodoCuota` a `Cuota` al momento de generarla.
3. Al crear un nuevo asociado, se generan automáticamente las cuotas que le corresponden según las [reglas de alta de asociado](altas-de-asociado.md).

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
