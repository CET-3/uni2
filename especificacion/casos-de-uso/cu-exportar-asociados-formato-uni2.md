---
type: "Caso de uso"
title: "CU-exportar-asociados-formato-uni2"
description: "Actor: Administrador"
tags: [mvp, caso-de-uso]
timestamp: 2026-06-22T00:00:00-03:00
---

# CU-exportar-asociados-formato-uni2

**Actor:** Administrador

**Alcance:** exportación disponible desde la consulta de asociados del backoffice. Permite descargar el padrón completo o los resultados filtrados de la búsqueda activa.

**Flujo principal:**

1.  El administrador entra a la consulta de asociados.
2.  Opcionalmente busca por DNI, número, apellido o nombre y aplica filtros estructurados.
3.  El administrador elige exportar asociados.
4.  El sistema descarga una planilla `.xlsx` con la hoja `ASOCIADOS`.
5.  Si había búsqueda o filtros activos, la planilla incluye solo esos resultados; si no había filtros, incluye el padrón completo.

**Columnas:** `numero_asociado`, `apellido`, `nombre`, `dni`, `tipo`, `email`, `telefono`, `direccion`, `curso_anio`, `curso_division`, `division`, `turno`, `curso_nombre`, `fecha_alta`, `fecha_inicio_cobro`, `estado`, `motivo_baja`.

**Decisión funcional:** `curso_nombre` es una ayuda visual para personas. El formato regular futuro de importación no debe depender de ese texto y debe usar los campos normalizados de curso.

**Restricción técnica:** la generación de planillas `.xlsx` usa la dependencia Python `openpyxl`, declarada en los archivos de dependencias del proyecto.

**Modelos afectados:** Asociado, Curso.
