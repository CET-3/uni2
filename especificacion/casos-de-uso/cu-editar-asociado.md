---
type: "Caso de uso"
title: "CU-editar-asociado"
description: "Actor: Gestión con permiso para editar asociados."
tags: [mvp, caso-de-uso]
timestamp: 2026-06-22T00:00:00-03:00
---

# CU-editar-asociado

**Actor:** Gestión con permiso para editar asociados.

**Alcance:** edición cotidiana desde una pantalla propia `gestion/asociados/<id>/editar/`. Incluye datos básicos, curso y fecha de inicio de cobro. No se usa el admin técnico para este flujo operativo.

**Flujo principal:**

1.  El usuario entra al detalle del asociado y elige `Editar asociado`.
2.  Modifica los campos necesarios.
3.  Guarda los cambios.
4.  El sistema conserva cuotas, pagos y usuario vinculado, muestra una confirmación y vuelve al detalle.

**Cancelación y errores:** `Cancelar` vuelve al detalle sin modificar datos. Si el formulario es inválido, permanece en edición con los valores ingresados. Tanto el detalle como la edición conservan el retorno a la consulta filtrada de origen.

**Permisos:** la pantalla de edición requiere permiso para editar asociados. Los usuarios con permiso solo de consulta pueden ver datos, deuda y pagos recientes, pero no modificar el asociado.

**Reglas relacionadas:** [Asociados](../reglas/asociados.md), [Altas de asociado](../reglas/altas-de-asociado.md).

**Modelos afectados:** Asociado, Curso.
