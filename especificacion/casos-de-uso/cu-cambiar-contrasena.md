---
type: "Caso de uso"
title: "CU-cambiar-contrasena"
description: "Actor: asociado autenticado que conoce su contraseña actual."
tags: [post-mvp, caso-de-uso, usuarios, asociados, diseno-aprobado]
timestamp: 2026-09-03T00:00:00-03:00
---

# CU-cambiar-contrasena

**Actor:** asociado autenticado que conoce su contraseña actual.

**Flujo principal:**

1. Abre `Cambiar contraseña` desde el menú de su cuenta.
2. Ingresa la contraseña actual, la contraseña nueva y su confirmación.
3. El sistema valida los tres valores con las reglas vigentes.
4. Guarda la contraseña nueva, mantiene abierta la sesión actual y muestra una
   confirmación.

Este recorrido no envía correo. Si la persona no conoce su contraseña actual,
debe usar [CU-recuperar-contrasena](cu-recuperar-contrasena.md).

**Situaciones especiales:** contraseña actual incorrecta, confirmación que no
coincide y cuenta sin asociado vinculado.

**Modelos afectados:** User.

**Reglas relacionadas:** [Usuarios](../reglas/usuarios.md).
