---
type: "Caso de uso"
title: "CU-dar-baja-asociado"
description: "Actor: Administrador"
tags: [mvp, caso-de-uso]
timestamp: 2026-06-22T00:00:00-03:00
---

# CU-dar-baja-asociado

**Actor:** Administrador

**Flujo principal:**

1.  Busca asociado.
2.  Selecciona baja.
3.  Carga fecha y motivo.
4.  El sistema cambia el estado a inactivo.
5.  Conserva cuotas y pagos.

**Reglas relacionadas:** [ASOCIADO-003](../reglas/asociados.md#asociado-003), [ASOCIADO-004](../reglas/asociados.md#asociado-004).

**Situaciones especiales:** baja con deuda, baja sin deuda, asociado con usuario.

**Modelos afectados:** Asociado.
