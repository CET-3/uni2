---
type: "Caso de uso"
title: "CU-editar-asociado"
description: "Actor: Gestión con permiso para editar asociados."
tags: [mvp, caso-de-uso]
timestamp: 2026-06-22T00:00:00-03:00
---

# CU-editar-asociado

**Actor:** Gestión con permiso para editar asociados.

**Alcance:** edición cotidiana desde una pantalla propia `gestion/asociados/<id>/editar/`. Incluye datos básicos, curso, estado, fecha de inicio de cobro y baja manual. No se usa el admin técnico para este flujo operativo.

**Flujo principal:**

1.  El usuario entra al detalle del asociado y elige editar datos.
2.  Modifica los campos necesarios.
3.  Si marca el asociado como inactivo, carga fecha y motivo de baja.
4.  Guarda los cambios.
5.  El sistema conserva cuotas, pagos y usuario vinculado.

**Permisos:** la pantalla de edición requiere permiso para editar asociados. Los usuarios con permiso solo de consulta pueden ver datos, deuda y pagos recientes, pero no modificar el asociado.

**Reglas relacionadas:** [ASOCIADO-003](/reglas/asociados.md#asociado-003), [ALTA-ASOCIADO-003](/reglas/altas-de-asociado.md#alta-asociado-003).

**Modelos afectados:** Asociado, Curso.
