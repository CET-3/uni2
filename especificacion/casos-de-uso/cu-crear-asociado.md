---
type: "Caso de uso"
title: "CU-crear-asociado"
description: "Actor: Gestión con permiso para editar asociados."
tags: [mvp, caso-de-uso]
timestamp: 2026-06-22T00:00:00-03:00
---

# CU-crear-asociado

**Actor:** Gestión con permiso para editar asociados.

**Alcance:** alta manual cotidiana desde `gestion/asociados/nuevo/`. No usa el admin técnico de Django.

**Flujo principal:**

1.  Carga datos personales.
2.  Selecciona el tipo. Si es `Asociado`, carga el curso; si es `Adherente`,
    elige una clasificación activa.
3.  El sistema asigna la fecha local del día como `fecha_alta`.
4.  El sistema calcula `fecha_inicio_cobro` según el tipo: dos meses antes para
    `Asociado` y el mismo mes para `Adherente`, sin usar un corte por día.
5.  Guarda el asociado.
6.  El sistema genera cuotas iniciales para los períodos activos existentes
    entre `fecha_inicio_cobro` y el mes del alta. También agrega períodos
    futuros activos que ya tengan `generado_el`.
7.  El sistema informa el alta y la cantidad de cuotas iniciales generadas.
8.  Siempre redirige al detalle operativo del asociado, donde la persona decide si quiere cobrar o editar.

**Reglas relacionadas:** [Asociados](../reglas/asociados.md), [Altas de asociado](../reglas/altas-de-asociado.md).

**Cancelación:** vuelve a `Atención al asociado` sin crear registros.

El formulario muestra y exige solamente el dato que corresponde al tipo. La
clasificación transitoria `Sin clasificar` no se ofrece en el alta manual.
`fecha_alta` y `fecha_inicio_cobro` no se muestran ni se aceptan como datos
editables en este flujo; permanecen disponibles en la edición administrativa y
en el admin técnico.

**Situaciones especiales:** DNI duplicado, curso inexistente, clasificación
inexistente o inactiva, asociado sin usuario, períodos faltantes o inactivos y
períodos futuros creados pero todavía no generados. Reintentar la operación no
duplica cuotas.

**Modelos afectados:** Asociado, Curso, ClasificacionAdherente, PeríodoCuota, Cuota.
