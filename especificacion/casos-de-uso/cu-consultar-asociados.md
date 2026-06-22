---
type: "Caso de uso"
title: "CU-consultar-asociados"
description: "Actor: Gestión"
tags: [mvp, caso-de-uso]
timestamp: 2026-06-22T00:00:00-03:00
---

# CU-consultar-asociados

**Actor:** Gestión

**Alcance:** listado operativo de asociados desde el backoffice, con búsqueda textual y filtros estructurados. La consulta y la exportación usan el mismo criterio de filtrado para evitar diferencias entre pantalla y descarga.

**Flujo principal:**

1.  El usuario entra a la consulta de asociados.
2.  Busca por DNI, número, apellido o nombre.
3.  Opcionalmente acota por estado, tipo, curso actual, con o sin usuario y con o sin deuda.
4.  El sistema muestra el listado filtrado.

**Filtros útiles:** estado, tipo, curso actual, presencia de usuario y presencia de deuda.

**Modelos afectados:** Asociado, Curso, Cuota.
