---
type: "Caso de uso"
title: "CU-crear-usuario-asociado"
description: "Actor: Administrador"
tags: [mvp, caso-de-uso]
timestamp: 2026-06-22T00:00:00-03:00
---

# CU-crear-usuario-asociado

**Actor:** Administrador

**Flujo principal:**

1.  Busca asociado.
2.  Verifica que no tenga usuario.
3.  Crea `User`.
4.  Lo vincula con `Asociado`.
5.  Lo agrega al grupo Asociados.

**Reglas relacionadas:** [Usuarios](../reglas/usuarios.md).

**Situaciones especiales:** asociado ya posee usuario, DNI inexistente, username duplicado, email vacío.

**Modelos afectados:** User, Asociado.
