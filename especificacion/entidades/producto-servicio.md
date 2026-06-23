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
- es_servicio*: indica si el ítem es un servicio. Si no se marca, se interpreta como producto.
- precio_asociados*: precio vigente para asociados.
- precio_no_asociados*: precio vigente para no asociados.
- activo*: indica si el producto o servicio se publica en el sitio.
- orden*: posición usada para ordenar productos y servicios dentro de su categoría.

**Restricciones de datos:** no puede repetirse el mismo nombre dentro de una misma categoría.

**Administración:** en el MVP se carga y edita desde el admin técnico de Django.

**Referencias funcionales:** ver [productos y servicios](../reglas/productos-servicios.md) y [CU-listar-productos-servicios-publicos](../casos-de-uso/cu-listar-productos-servicios-publicos.md).
