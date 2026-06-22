---
type: "Entidad"
title: "Curso"
description: "Representa un curso comisión de la escuela."
resource: "asociados.models.Curso"
tags: [mvp, modelo-de-datos]
timestamp: 2026-06-22T00:00:00-03:00
status: "listo"
---

# Curso

Representa un curso comisión de la escuela.

**Campos:**

- id\*: identificador interno del curso.
- año\*: año del curso, ej: 1ro, 2do, 3ro. Texto ingresable.
- curso\*: división o comisión del año, ej: 1ra, 2da, 3ra. Texto ingresable.
- división\*: ciclo al que pertenece: CB (Ciclo Básico) o CS (Ciclo Superior).
- turno\*: turno: TM (Turno Mañana) o TT (Turno Tarde).
- activo\*: indica si el curso está activo en el sistema.

**Unicidad:** un solo curso por combinación de año, curso, división y turno.

**Ejemplo:** 2do 1ra CB TT = segundo año, primera división, Ciclo Básico, Turno Tarde.

**Notas:** en el MVP, los cursos se administran desde el admin técnico de Django. En listados, formularios y pantallas operativas se muestran con las constantes cortas, por ejemplo `2do 1ra CB TT`, para evitar textos largos.
