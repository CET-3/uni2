---
type: "Pantalla"
title: "Atención diaria"
description: "Control operativo de ingresos y pendientes de atención."
tags: [gestion, pantalla, pagos]
timestamp: 2026-09-10T00:00:00-03:00
---

# Atención diaria

Entrada `/gestion/atencion-diaria/`, disponible desde la home administrativa
según permisos, sin reemplazar `Atención al asociado` ni la bandeja de solicitudes.
No tiene buscador de asociados ni botón general para buscar o registrar cobros.

## Composición

- Encabezado operativo compartido `uni2-compact-hero`, sin kicker ni breadcrumbs
  que repitan el título de esta entrada de primer nivel.
- Filtros por fecha del pago y operador, desde/hasta para rango personalizado,
  botón Aplicar y errores junto a cada campo. Funciona sin JavaScript.
- Tres tarjetas: total cobrado, efectivo y billetera virtual; muestran importes
  argentinos con dos decimales y cantidades de pagos.
- Una línea de composición distingue cuotas/recargos de donaciones, ambas
  incluidas en el total. No agrega tarjetas ni gráficos anidados.
- Tabla paginada de pagos: persona y tipo, fecha, medio, importe y operador.
  Una fila corresponde a un pago, aunque cubra varias cuotas. Su único enlace
  abre el detalle del pago.
- Con los permisos correspondientes: solicitudes pendientes actuales con
  enlaces por estado, y altas del período con su listado. Los dos bloques
  indican que abarcan todo el equipo, aun cuando se consultan cobros propios.
- Resumen separado de pagos históricos sin fecha de cobro confirmada: cantidad
  e importe por fecha de referencia y operador, excluidos de las cards y del
  listado de cobros. No cambia el estado pagado de las cuotas.
- Alertas compartidas para pagos inconsistentes y
  creaciones auditadas con una fecha distinta del pago.

## Detalles

- `/gestion/atencion-diaria/pagos/<id>/`: identifica pago y persona, fecha
  efectiva y fecha de carga cuando se conoce, operador, medio, total recibido,
  aplicaciones por cuota y donaciones. Enlaza la ficha sólo si está autorizada.
- `/gestion/atencion-diaria/altas/`: listado paginado por fecha de alta, tipo y
  curso/clasificación, con enlace a las fichas existentes.
- `/gestion/atencion-diaria/cargas/`: lista paginada de pagos cargados con otra
  fecha, con fecha y hora de carga visibles.

Los detalles usan breadcrumbs compartidos para volver al tablero con filtros.
No incorporan controles de edición ni registran pagos. El enlace a la ficha
continúa el recorrido operativo habitual del proyecto.

## Design system y privacidad

Se extiende `base.html` y se reutilizan sus navbar, footer, temas y PWA. Las
tarjetas usan `uni2-metric-card`/`uni2-surface-card`, los datos de detalle
`uni2-data-list` y las alertas `components/alert.html`. Las tablas de registros
usan `uni2-records-table`, conservan semántica y se apilan bajo `md`; no se
ocultan datos de pago en móvil. Las grillas y controles son Bootstrap 5.

No se copia CSS de la maqueta ni se crea una hoja paralela. Los acentos de marca
son azul para total, verde para efectivo y amarillo para billetera, como en la
maqueta aprobada. Se usan variantes `brand-blue`, `brand-green` y `brand-yellow`:
identifican categorías, no éxito o advertencia. Solicitudes y Ver nuevas altas
usan `uni2-summary-link`: texto neutro sin subrayado, flecha, foco visible y
zona táctil de al menos 44 px; las solicitudes agregan un contador neutro.
Las métricas usan la variante `uni2-metric-card-overview`: títulos en mayúscula
inicial, importe destacado, borde superior fino e iconos Bootstrap decorativos
arriba a la derecha (`arrow-down-left`, `currency-dollar`, `wallet2`). Se conservan
dos decimales en los importes reales aunque la maqueta use números enteros.
Las respuestas requieren conexión y no se cachean como
documentos privados. Ver [design system](../arquitectura/design-system.md).

Las fórmulas, permisos y límites se definen en
[Atención diaria](../reglas/atencion-diaria.md).
