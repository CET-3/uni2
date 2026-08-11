---
type: "Caso de uso"
title: "CU-iniciar-sesion-elegir-experiencia"
description: "Actor: Persona con una cuenta activa de Uni2."
tags: [mvp, caso-de-uso, usuarios]
timestamp: 2026-08-10T00:00:00-03:00
---

# CU-iniciar-sesion-elegir-experiencia

**Actor:** persona con una cuenta activa de Uni2.

**Flujo principal:**

1. La persona abre el formulario de ingreso.
2. Ingresa su usuario y contraseña.
3. El sistema valida las credenciales y vuelve a la home o a la URL segura que
   originó el ingreso.
4. Si tiene una sola experiencia, la home muestra directamente sus acciones.
5. Si tiene dos o más, la home muestra `Elegí cómo querés ingresar`.
6. La persona elige asociado, comercio o administración.
7. El sistema muestra solamente acciones autorizadas para esa experiencia.
8. Al cerrar sesión, vuelve a la home pública y elimina la información privada
   conservada por la PWA.

**Situaciones especiales:** credenciales inválidas, cuenta inactiva, perfil
solicitado no autorizado, grupo de asociado o comercio sin entidad vinculada y
URL de retorno externa o insegura.

**Modelos afectados:** Usuario, Asociado y Comercio.

**Reglas relacionadas:** [Usuarios](../reglas/usuarios.md) y
[PWA](../reglas/pwa.md).
