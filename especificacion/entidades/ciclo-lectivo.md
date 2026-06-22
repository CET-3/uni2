---
type: "Entidad"
title: "CicloLectivo"
description: "Representa un año lectivo. Se usa como referencia en inscripciones y períodos de cuota."
resource: "asociados.models.CicloLectivo"
tags: [mvp, modelo-de-datos]
timestamp: 2026-06-22T00:00:00-03:00
status: "listo"
---

# CicloLectivo

Representa un año lectivo. Se usa como referencia en inscripciones y períodos de cuota.

**Campos:**

- id\*: identificador interno del ciclo lectivo.
- año\*: año del ciclo lectivo. Único en el sistema.

**Uso operativo:** se carga desde el admin técnico de Django. La pantalla de períodos de cuota usa ciclos lectivos ya existentes.

**Referencias funcionales:** ver [altas de asociado](../reglas/altas-de-asociado.md) y [generar período de cuota](../casos-de-uso/cu-generar-periodo-cuota.md).
