---
type: "Regla de negocio"
title: "Comercios"
description: "Reglas de negocio sobre comercios."
tags: [mvp, reglas]
timestamp: 2026-06-22T00:00:00-03:00
---

# Comercios

## COMERCIO-002

El beneficio del comercio se guarda como texto libre dentro de `Comercio`.

## COMERCIO-003

El estado del comercio se selecciona desde una lista fija definida en el sistema. No se administra como entidad independiente.

## COMERCIO-004

Solo comercios con estado firmado pueden validar credenciales.

## COMERCIO-005

En el MVP, la carga y edición de comercios se realiza desde el admin técnico de Django. No se implementa una pantalla propia de gestión de comercios en el backoffice `gestion`.

## COMERCIO-006

En el MVP, la carga y edición de actividades comerciales se realiza desde el admin técnico de Django. No se implementa una pantalla propia de gestión de `ActividadComercial` en el backoffice `gestion`.

## COMERCIO-007

En el admin técnico, la selección de `usuario` para `Comercio` debe usar búsqueda/autocompletado para soportar muchos usuarios. El listado de comercios debe mostrar todos los atributos, empezando por los obligatorios.
