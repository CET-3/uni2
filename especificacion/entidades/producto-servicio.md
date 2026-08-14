---
type: "Entidad"
title: "ProductoServicio"
description: "Representa un producto o servicio publicado por la mutual."
resource: "contenidos.models.ProductoServicio"
tags: [mvp, entidad]
timestamp: 2026-06-23T00:00:00-03:00
---

# ProductoServicio

Representa un producto o servicio publicado por la mutual en el sitio público.

**Campos:**

- id*: identificador interno del producto o servicio.
- categoría*: categoría pública a la que pertenece.
- nombre*: nombre visible.
- descripción*: texto público que explica qué incluye.
- foto: fotografía propia para la fila del catálogo y la ficha individual.
- es_servicio*: indica si el ítem es un servicio. Si no se marca, se interpreta como producto.
- ciclo_destinatario: ciclo escolar al que se dirige, tomado de los valores de `Curso.division`.
- curso_destinatario: año dentro del ciclo, tomado de `Curso.anio` sin distinguir comisión ni turno.
- precio_asociados: precio vigente para asociados, cuando corresponde.
- precio_no_asociados: precio vigente para no asociados, cuando corresponde.
- activo*: indica si el producto o servicio se publica en el sitio.
- orden*: posición usada para ordenar productos y servicios dentro de su categoría.

**Restricciones de datos:** no puede repetirse el mismo nombre dentro de una
misma categoría. Puede indicarse ciclo sin curso, pero no curso sin ciclo. Los
importes informados deben ser mayores que cero. Un producto requiere precio
para asociados; un servicio puede tener ambos precios vacíos. Nunca puede
informarse precio para no asociados sin precio para asociados.

**Escenarios de precio:** dos importes diferentes representan precio
diferenciado; dos importes iguales representan un precio único; solo precio
para asociados representa venta exclusiva a asociados; ambos importes vacíos
representan un servicio sin precio.

**Administración:** en el MVP se carga y edita desde el admin técnico de
Django. Las opciones de ciclo y curso se deducen de combinaciones existentes
en cursos activos y eliminan diferencias de comisión y turno.

**Referencias funcionales:** ver [productos y servicios](../reglas/productos-servicios.md) y [CU-listar-productos-servicios-publicos](../casos-de-uso/cu-listar-productos-servicios-publicos.md).
