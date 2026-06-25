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
7.  Si la persona de gestión también tiene permiso para cobrar cuotas, redirige a la pantalla de cobro con el asociado preseleccionado.
8.  Si no tiene permiso para cobrar cuotas, redirige al detalle operativo del asociado.

**Reglas relacionadas:** [Asociados](../reglas/asociados.md), [Altas de asociado](../reglas/altas-de-asociado.md).

**Situaciones especiales:** DNI duplicado, curso inexistente, alta después del día 15, asociado sin usuario, períodos de cuota faltantes, usuario sin permiso para cobrar cuotas.

**Modelos afectados:** Asociado, Curso, PeríodoCuota, Cuota.
