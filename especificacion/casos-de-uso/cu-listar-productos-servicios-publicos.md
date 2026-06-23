---
type: "Caso de uso"
title: "CU-listar-productos-servicios-publicos"
description: "Actor: Visitante"
tags: [mvp, caso-de-uso]
timestamp: 2026-06-23T00:00:00-03:00
status: "listo"
---

# CU-listar-productos-servicios-publicos

**Actor:** Visitante

**Flujo principal:**

1.  Ingresa a la home.
2.  Selecciona el acceso a productos y servicios.
3.  El sistema muestra las categorías activas ordenadas.
4.  Dentro de cada categoría, el sistema muestra los productos y servicios activos ordenados.
5.  Para cada producto o servicio, el sistema muestra nombre, descripción, si es producto o servicio, precio para asociados y precio para no asociados.
6.  Si la categoría tiene texto de call to action, el sistema lo muestra debajo del listado y convierte emails o URLs en enlaces.
7.  Desde una publicidad o un enlace público, el visitante puede abrir el detalle de un producto o servicio activo.

**Reglas relacionadas:** [PRODUCTO-SERVICIO-001](../reglas/productos-servicios.md#producto-servicio-001), [PRODUCTO-SERVICIO-002](../reglas/productos-servicios.md#producto-servicio-002), [PRODUCTO-SERVICIO-003](../reglas/productos-servicios.md#producto-servicio-003).

**Modelos afectados:** CategoriaProductoServicio, ProductoServicio.
