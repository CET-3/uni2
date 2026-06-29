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

**Creación masiva desde importación:** desde la pantalla `Importar padrón inicial`, el administrador puede ejecutar `Crear usuarios faltantes`. Esta acción crea usuarios para todos los asociados sin usuario vinculado. El `username` inicial y la contraseña inicial son el DNI del asociado. Si ya existe un `User` con ese username y no está vinculado a otro asociado, el sistema lo vincula al asociado en lugar de crear uno nuevo. Si el usuario existente ya pertenece a otro asociado, registra el error y continúa con el resto. La acción informa cuántos usuarios creó, cuántos usuarios existentes vinculó y cuántos asociados ya tenían usuario antes de ejecutarla.

**Reglas relacionadas:** [Usuarios](../reglas/usuarios.md).

**Situaciones especiales:** asociado ya posee usuario, DNI inexistente, username duplicado vinculado a otro asociado, email vacío, creación masiva con errores parciales.

**Modelos afectados:** User, Asociado.
