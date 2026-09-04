---
type: "Caso de uso"
title: "CU-importar-padron-inicial"
description: "Actor: Administrador de la app"
tags: [mvp, caso-de-uso]
timestamp: 2026-06-22T00:00:00-03:00
---

# CU-importar-padron-inicial

**Actor:** Administrador de la app (`is_superuser`)

**Alcance:** importación inicial para la puesta en marcha desde la planilla heredada. No define el formato regular futuro de intercambio de datos.

**Permiso:** `gestion.importar_asociados`, reservado al superusuario. No se
asigna a Atención al asociado ni al Administrador de la mutual.

**Flujo principal:**

1.  Sube la planilla heredada en formato `.xlsx` con la hoja `PADRÓN GENERAL`.
2.  El sistema analiza la planilla sin guardar datos.
3.  El sistema clasifica filas como `IMPORTAR`, `REVISAR` o `NO IMPORTAR`.
4.  El sistema muestra resumen, filas a revisar, la clasificación interpretada
    para cada adherente y los cursos nuevos que se crearían.
5.  El sistema explica el criterio de cada estado para que el administrador entienda por qué algunas filas no se importan.
6.  La previsualización queda guardada temporalmente en la sesión del usuario.
7.  Si hay filas a revisar, el administrador puede descargar una planilla `.xlsx` con la hoja `PADRÓN GENERAL`, solo con esas filas, una primera columna `Fila original`, la columna `Número de asociado` y una columna final con el motivo de revisión.
8.  El administrador confirma la importación.
9.  El sistema importa solo las filas `IMPORTAR`, crea cursos faltantes y omite las filas a revisar.

**Reglas relacionadas:** [Asociados](../reglas/asociados.md), [Cursos](../reglas/cursos.md).

**Reglas de importación:** la primera palabra de `Apellido/nombre` se toma como apellido y el resto como nombre. Si falta nombre se completa con `[completar]`. Si no se pueden deducir año, división, ciclo y turno del curso, la fila queda para revisar. Para un adherente, los cargos conocidos se normalizan a una clasificación activa: Docente, Preceptor, Directivo, Auxiliar, Biblioteca, Padrino mutual, Particular, Familiar o Estudiante. Un cargo desconocido o vacío queda para revisar. Si la planilla no indica turno y el curso es completo, se usa `TM` como valor provisorio y se lista el curso antes de confirmar.

Si una fila declara tipo `Asociado` y contiene un curso válido, prevalecen ese
tipo y ese curso. Si declara `Asociado` pero contiene un cargo en lugar de un
curso, no se convierte automáticamente en adherente: queda para revisar.

**Corrección de ciclo:** CB no tiene 3ro ni 4to. Si la planilla indica CB para un curso de 3er o 4to año, el sistema lo corrige automáticamente a CS y lo registra como observación.

**Orden de cursos:** los cursos nuevos se muestran ordenados por ciclo, año, división y turno para facilitar la revisión antes de confirmar.

**Restricción técnica:** la lectura de planillas `.xlsx` usa la dependencia Python `openpyxl`, declarada en los archivos de dependencias del proyecto.

**Fechas:** `fecha_alta` se carga automáticamente con la fecha del día de la importación. `fecha_inicio_cobro` se carga automáticamente con el 1 de marzo de 2026 para todos los asociados importados desde el padrón inicial.

**Usuarios de asociados:** la importación no crea usuarios de acceso. Esto mantiene la confirmación del padrón dentro de un tiempo razonable para entornos con timeout, como Vercel. Después de importar, el administrador puede usar la acción `Crear usuarios faltantes` desde la pantalla de importación para crear los `User` de Django de asociados que todavía no tengan usuario vinculado. Esa acción procesa usuarios por tandas y puede repetirse hasta completar todo el padrón.

**Duplicados de DNI:** si dos filas tienen el mismo DNI y el mismo nombre completo, se considera una repetición involuntaria en la planilla: solo se importa la primera fila y las siguientes se descartan. Si tienen el mismo DNI pero distinto nombre, la fila queda para revisar por DNI duplicado real.

**Número de asociado:** el sistema ignora la columna de número de asociado de la planilla original. Al confirmar la importación, el campo `numero_asociado` se asigna automáticamente (secuencia incremental). Si la planilla tiene un valor no numérico, se registra como observación sin bloquear la importación.

**Situaciones especiales:** curso incompleto, asociado ya existente, email faltante, teléfono faltante, tipo inválido.

**Modelos afectados:** Asociado, Curso, ClasificacionAdherente.
