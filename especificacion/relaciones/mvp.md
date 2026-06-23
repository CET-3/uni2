---
type: "Relación"
title: "Relaciones del MVP"
description: "Relaciones entre entidades del MVP."
tags: [mvp, modelo-de-datos]
timestamp: 2026-06-22T00:00:00-03:00
---

# Relaciones del MVP

- Usuario 1 - 0..1 Asociado
- Curso 1 - N Asociado como curso_actual
- PeríodoCuota 1 - N Cuota
- Asociado 1 - N Cuota
- Asociado 1 - N Pago
- Pago 1 - N PagoCuota
- Cuota 1 - N PagoCuota
- CicloLectivo 1 - N PeríodoCuota
- ActividadComercial 1 - N Comercio
- Usuario 1 - 0..1 Comercio
- CategoriaProductoServicio 1 - N ProductoServicio
