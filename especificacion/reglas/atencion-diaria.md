---
type: "Regla de negocio"
title: "Atención diaria"
description: "Períodos, ingresos, permisos y límites del control operativo."
tags: [reglas, gestion, pagos]
timestamp: 2026-09-10T00:00:00-03:00
---

# Atención diaria

## ATENCION-001 — Período de consulta

El tablero toma `Hoy` por defecto. `Ayer` corresponde al día local anterior;
`Esta semana` empieza el lunes y termina hoy, incluso si cruza de mes o año.
El rango personalizado incluye ambas fechas y exige inicio <= fin <= hoy.
Las fechas se interpretan en el timezone activo de Django, configurado para
Argentina. Los campos desde/hasta sólo determinan el rango personalizado.

Filtros inválidos no muestran resultados ni se reemplazan silenciosamente por
una consulta más amplia. Cambiar filtros vuelve a la primera página.

## ATENCION-002 — Dinero recibido

Los ingresos se seleccionan por **`Pago.fecha`**, no por período de cuota ni por
fecha de carga. Una cuota de agosto pagada en septiembre suma a los ingresos
de septiembre. No se calcula cumplimiento ni se proyecta recaudación.
Se excluyen las importaciones históricas identificadas en ATENCION-005: no
aportan importes, cantidades ni aplicaciones a estos indicadores o al listado
principal porque no tienen una fecha efectiva de cobro confirmada.

| Indicador | Cálculo sobre los pagos del período y operador autorizado |
| --- | --- |
| Total cobrado | Suma de `Pago.importe` |
| Efectivo | Total de pagos con método efectivo |
| Billetera virtual | Total de pagos con ese método |
| Cantidad de pagos | Cantidad de registros `Pago`, no cantidad de cuotas |
| Cuotas y recargos | Suma de las aplicaciones `PagoCuota.importe` |
| Donaciones | Suma de `Donacion.importe` vinculadas a esos pagos |

Las donaciones ya forman parte del total recibido; no se suman nuevamente.
Las aplicaciones a cuotas incluyen la mora cobrada: no se separa capital y
recargo porque la aplicación no conserva esa discriminación.

Las sumas de aplicaciones y donaciones se calculan independientemente para no
multiplicar importes cuando ambas relaciones contienen varias filas.
Si un pago no coincide con la suma de sus aplicaciones y donaciones, se muestra
una advertencia y se conserva su importe registrado. No se asigna automáticamente
la diferencia a cuotas ni se permite compensar inconsistencias entre pagos.
Un período vacío presenta importes cero y una lista vacía.

## ATENCION-003 — Alcance por permisos

- `gestion.ver_atencion_diaria` habilita el tablero, el detalle de pagos propios
  y la consulta de sus creaciones auditadas con fecha distinta.
- `gestion.ver_cobros_equipo` permite ampliar ese alcance a todo el equipo,
  incluidos pagos sin operador registrado; por sí solo no habilita el tablero.
- Atención al asociado recibe el primer permiso y comienza en `Mis cobros`.
  Administrador de la mutual recibe ambos y comienza en `Todo el equipo`.
- `Mis cobros` significa `Pago.registrado_por = usuario autenticado`; no se
  deduce de la persona asociada, del actor de otra operación o de `is_staff`.
- Altas y enlaces a fichas requieren `gestion.consultar_asociados`.
  Solicitudes requieren `gestion.consultar_solicitudes_asociacion`.
- El detalle valida el alcance del pago en el servidor, aunque se acceda
  directamente por URL. Ninguno de estos permisos habilita registrar un cobro.

## ATENCION-004 — Altas y pendientes

Las altas se cuentan por `Asociado.fecha_alta` dentro del rango inclusivo, con
separación entre asociados y adherentes, independientemente de su estado actual.
Incluyen las altas manuales y las originadas en solicitudes. No se filtran por
operador de cobros; el bloque indica `Todo el equipo`.

Las solicitudes pendientes muestran los estados actuales `recibida`,
`datos_aprobados` y `observada`, sin filtro temporal ni de cobrador. Cada conteo
enlaza a la bandeja existente filtrada por estado. No incluye solicitudes
canceladas o con alta completada. Esto no es el análisis de conversión de
solicitudes previsto en Métricas.

## ATENCION-005 — Fecha de pago y fecha de carga

La primera creación auditada de `cuotas.Pago` permite conocer su fecha y hora
de carga. Sin esa evidencia se muestra `Sin fecha de carga auditada`; nunca se
reemplaza por la fecha de pago. La consulta no concede acceso a la auditoría
general ni expone los datos de otros eventos.

El aviso de pagos cargados con otra fecha selecciona creaciones cuyo día local
pertenece al rango elegido y difiere de `Pago.fecha`. Respeta el mismo alcance
de operador. Permite revisar pagos cargados durante el período que, por su fecha
efectiva, se cuentan en otro día. También detecta discrepancias entre días de
un mismo rango; su listado muestra ambas fechas.

Las importaciones heredadas conocidas se identifican por la observación que
escribe el importador de cuotas históricas. Ese importador asigna el día 10 del
mes de la cuota como fecha del pago, sin confirmar cuándo se recibió el dinero.
Se excluyen de los cobros operativos y del aviso de cargas con otra fecha.
Un bloque independiente, `Pagos históricos sin fecha de cobro confirmada`,
muestra cantidad e importe con el mismo alcance de operador y el rango aplicado
a su fecha de referencia. No debe interpretarse como dinero ingresado en ese
rango. No modifica pagos, aplicaciones, estado de cuotas ni cálculo de deuda;
las cuotas históricas pagadas siguen pagadas. El bloque se oculta si no hay
importados en ese rango y alcance.
La falta de auditoría o de información original no se resuelve con una fecha
estimada. El aviso no detecta cargas externas que carezcan de esa identificación.

## ATENCION-006 — Consulta, no caja

El tablero y sus detalles son de solo lectura. No registran apertura, egresos,
arqueo ni saldo físico de caja. El efectivo cobrado es un ingreso registrado.
Pagos y altas se paginan de a 25 registros y los totales abarcan toda la consulta,
no sólo la página visible. Las respuestas privadas usan `no-store` y no se
agregan al almacenamiento offline de la PWA.
