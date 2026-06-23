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
