---
type: "Regla de negocio"
title: "Productos y servicios"
description: "Reglas de negocio sobre productos y servicios publicados por la mutual."
tags: [mvp, reglas]
timestamp: 2026-06-23T00:00:00-03:00
---

# Productos y servicios

## PRODUCTO-SERVICIO-001

El sitio público muestra solamente categorías activas y productos o servicios activos.

## PRODUCTO-SERVICIO-002

Las categorías se muestran ordenadas por `orden` y luego por `nombre`. Los productos y servicios se muestran dentro de su categoría ordenados por `orden` y luego por `nombre`.

## PRODUCTO-SERVICIO-003

El texto de call to action pertenece a la categoría y es texto libre. La vista pública debe convertir emails y URLs en enlaces al renderizarlo.

## PRODUCTO-SERVICIO-004

En el MVP, la carga y edición de categorías, productos y servicios se realiza desde el admin técnico de Django. No se implementa una pantalla propia de gestión en el backoffice `gestion`.

## PRODUCTO-SERVICIO-005

El destinatario escolar es opcional. Un ítem sin ciclo ni curso es general; un
ítem con ciclo y sin curso se dirige a todo el ciclo; un ítem con ambos valores
se dirige a ese año dentro del ciclo. No se permite curso sin ciclo. El admin
toma las combinaciones de los cursos activos y no distingue comisión ni turno.

## PRODUCTO-SERVICIO-006

Los dos campos de precio representan cuatro escenarios:

1. ambos informados y diferentes: precio diferenciado;
2. ambos informados e iguales: precio único;
3. solo precio para asociados: venta exclusiva a asociados;
4. ambos vacíos: servicio sin precio.

Los importes informados deben ser mayores que cero. Un producto no puede quedar
sin precio y nunca puede existir precio para no asociados sin precio para
asociados. La ausencia de precio se representa con campos vacíos, no con cero.

## PRODUCTO-SERVICIO-007

La ficha de categoría agrupa primero los ítems generales y luego los destinados
a Ciclo Básico y Ciclo Superior, que se presentan como grupos principales.
Dentro de cada ciclo muestra primero los ítems para todo el ciclo y después los
años con la forma `1.º C.B.`, `2.º C.B.`, `1.º C.S.` y equivalentes. En cada
grupo conserva `orden` y `nombre`. Si se mezclan escenarios de precio, usa
tablas consecutivas con encabezados compatibles sin reordenar los ítems. En
mobile se puede alternar entre ciclos cuando existen ambos; los ítems generales
quedan fuera de esa selección.

## PRODUCTO-SERVICIO-008

Cada producto o servicio puede tener una foto opcional. La categoría puede
tener una imagen informativa compartida con título configurable. No se reservan
espacios vacíos cuando faltan imágenes. La fila del catálogo abre la ficha
individual, donde la foto propia se muestra en tamaño grande.

## PRODUCTO-SERVICIO-009

En las tablas públicas, el encabezado de nombres se deduce de `es_servicio`:
`Producto` cuando todos son productos, `Servicio` cuando todos son servicios y
`Producto o servicio` cuando conviven ambos tipos. Las columnas monetarias se
alinean a la derecha. Un grupo compuesto íntegramente por servicios sin precio
no muestra una columna vacía de precio o disponibilidad.

## PRODUCTO-SERVICIO-010

El nombre de un producto o servicio es el texto que se muestra en el catálogo,
pero no es único. Se permiten varios ítems con el mismo nombre, también dentro
de una misma categoría. La descripción es opcional y, cuando no se informa, la
presentación pública omite ese texto sin impedir guardar el ítem.
