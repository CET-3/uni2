---
type: "Entidad"
title: "ClasificacionAdherente"
description: "Clasifica la relación institucional de una persona adherente."
resource: "asociados.models.ClasificacionAdherente"
tags: [mvp, modelo-de-datos]
timestamp: 2026-08-21T00:00:00-03:00
---

# ClasificacionAdherente

Catálogo administrable que clasifica a una persona de tipo adherente.

**Campos:**

- id\*: identificador interno.
- nombre\*: nombre visible y único.
- activa\*: indica si puede asignarse en nuevas altas y ediciones.
- orden\*: posición en formularios y listados.

**Valores iniciales:** Docente, Preceptor, Directivo, Auxiliar, Biblioteca,
Padrino mutual, Particular, Familiar, Estudiante y Sin clasificar.

**Administración:** se gestiona desde el admin técnico. Una clasificación en
uso no se elimina; puede desactivarse. `Sin clasificar` es transitoria para
datos heredados y no se ofrece en altas manuales.
