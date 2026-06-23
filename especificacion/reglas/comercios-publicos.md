---
type: "Regla de negocio"
title: "Comercios públicos"
description: "Reglas de negocio sobre publicación y visualización de comercios."
tags: [mvp, reglas]
timestamp: 2026-06-22T00:00:00-03:00
---

# Comercios públicos

Estas reglas describen cómo se cargan, mantienen y muestran los comercios adheridos
en el sitio público.

## COMERCIO-PUBLICO-001

En el sitio público se muestran los comercios con estado `Firmado`.

## COMERCIO-PUBLICO-002

El estado del comercio se selecciona desde una lista fija definida en el sistema.
No se administra como entidad independiente.

## COMERCIO-PUBLICO-003

En el MVP, la gestión de comercios se realiza desde el admin técnico de Django.

## COMERCIO-PUBLICO-004

Los comercios publicados se listan de acuerdo al atributo `orden`.
