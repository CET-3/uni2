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
2.  Selecciona `Productos y servicios` en la navegación y el sistema lo ubica en `/#productos-servicios`.
3.  El sistema muestra las categorías activas ordenadas.
4.  Dentro de cada categoría, el sistema muestra los productos y servicios
    activos. Presenta primero los generales; luego separa Ciclo Básico y Ciclo
    Superior y, dentro de cada ciclo, los productos para todo el ciclo y los
    cursos. En mobile permite elegir un ciclo cuando existen ambos.
5.  Cada fila muestra nombre, foto si existe y el escenario de precio que
    corresponda: diferenciado, único, solo asociados o servicio sin precio. La
    tabla identifica si contiene productos, servicios o ambos; al no existir
    precios, omite por completo esa columna.
6.  Seleccionar la fila abre la ficha individual del producto o servicio.
7.  La ficha individual muestra descripción, destinatario, la foto grande
    debajo de esos datos y precios o condiciones según corresponda. La vuelta
    se resuelve con el breadcrumb, sin un botón redundante.
8.  Si la categoría tiene imagen informativa titulada, el sistema la muestra
    debajo de los precios de la categoría y también en la ficha individual.
9.  Si la categoría tiene texto de call to action, el sistema lo muestra
    debajo del contenido y convierte emails o URLs en enlaces.

La ruta `/productos-servicios/` se conserva por compatibilidad, pero no forma parte de la navegación principal.

**Reglas relacionadas:** [Productos y servicios](../reglas/productos-servicios.md).

**Modelos afectados:** CategoriaProductoServicio, ProductoServicio.
