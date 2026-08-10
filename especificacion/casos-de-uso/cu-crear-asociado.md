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
2.  Selecciona tipo y curso si corresponde.
3.  Define fecha de alta.
4.  El sistema calcula `fecha_inicio_cobro` según la fecha de alta.
5.  Guarda el asociado.
6.  El sistema genera cuotas iniciales para los períodos de cuota existentes entre `fecha_inicio_cobro` y la fecha de alta.
7.  El sistema informa el alta y la cantidad de cuotas iniciales generadas.
8.  Siempre redirige al detalle operativo del asociado, donde la persona decide si quiere cobrar o editar.

**Reglas relacionadas:** [Asociados](../reglas/asociados.md), [Altas de asociado](../reglas/altas-de-asociado.md).

**Cancelación:** vuelve a `Atención al asociado` sin crear registros.

**Situaciones especiales:** DNI duplicado, curso inexistente, alta después del día 15, asociado sin usuario y períodos de cuota faltantes.

**Modelos afectados:** Asociado, Curso, PeríodoCuota, Cuota.
