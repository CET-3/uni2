---
type: "Regla de negocio"
title: "Usuarios"
description: "Reglas de negocio sobre usuarios."
tags: [mvp, reglas]
timestamp: 2026-06-22T00:00:00-03:00
---

# Usuarios

## USUARIO-001

Crear asociado no crea automáticamente un usuario.

## USUARIO-002

El administrador puede crear un usuario para un asociado existente.

## USUARIO-003

No se puede crear un nuevo usuario para un asociado que ya tiene uno vinculado.

## USUARIO-004

El username puede ser el DNI.

## USUARIO-005

El listado de asociados debe mostrar si tiene usuario y el ultimo acceso usando `User.last_login`.

## USUARIO-006

En el admin técnico de Django, el listado de usuarios debe mostrar los grupos asignados para facilitar la operación de roles.

## USUARIO-007

El panel de asociado se habilita por vínculo con `Asociado`, el panel de comercio por vínculo con `Comercio` y el panel de gestión por permisos operativos de la app `gestion`.

## USUARIO-008

Si un usuario tiene más de una experiencia disponible, luego del login ve una pantalla para elegir entre asociado, comercio y gestión.

## USUARIO-009

`is_staff` habilita el admin técnico de Django, pero no define por sí solo qué tareas operativas puede usar una persona en `gestion`. Las pantallas y accesos del backoffice se controlan con permisos Django propios de la app `gestion`.

## USUARIO-010

El grupo `Atención de mutual` representa a estudiantes que atienden la mutual. Tiene permisos para ver gestión, consultar y editar asociados, cobrar cuotas y ver la especificación del proyecto. No incluye importaciones, exportaciones, deudores ni administración de períodos de cuota. En la carga inicial, el usuario `atencion` también queda vinculado a un asociado de prueba para poder probar el selector de paneles.

## USUARIO-011

El sistema define tres grupos base: `asociado`, `comercio` y `gestion`. La data migration `0002_crear_grupos_y_permisos` los crea y asigna todos los permisos de la app `gestion` al grupo `gestion`. El comando `carga_inicial` puede asignar subconjuntos (ej. grupo `Atención de mutual`).

## USUARIO-012

`create_user_for_comercio(comercio, password)` en `usuarios/services.py` crea un usuario Django, lo vincula al comercio y lo asigna al grupo `comercio`. El username se genera como `com-{id}`. Rechaza con `ValueError` si el comercio ya tiene usuario.

## USUARIO-013

`GestionCrearUsuarioAsociadoView` en `gestion/views.py` permite a un usuario con permiso `editar_asociados` crear un usuario para un asociado desde la pantalla de detalle. Usa el DNI como username por defecto. Redirige al detalle con mensaje de éxito o error. GET redirige sin acción.

## USUARIO-014

`GestionCrearUsuariosAsociadosFaltantesView` en `gestion/views.py` permite a un usuario con permiso `importar_asociados` crear usuarios para todos los asociados sin usuario vinculado desde la pantalla de importación de padrón. Usa el DNI como username y contraseña inicial. Si ya existe un usuario con username igual al DNI y no está vinculado a otro asociado, lo vincula al asociado. Si un asociado falla, registra el error y sigue con los demás. La acción es idempotente: si se ejecuta otra vez, no duplica usuarios ya vinculados.

## USUARIO-015

El `GestionPermissionRequiredMixin` usa `UserPassesTestMixin` con `raise_exception = True` para rechazar con 403 en lugar de redirigir al login. Las vistas deben declarar su lógica en métodos `get()`/`post()` y no en `dispatch()` para que el permiso se evalúe antes.

## USUARIO-016

La especificación del proyecto se sirve en `/especificacion/` y requiere el permiso `gestion.ver_especificacion`. Usa un mixin propio `VerEspecificacionRequiredMixin` que verifica ese permiso. En la carga inicial, el permiso se asigna al grupo `Atención de mutual` y a `Administradores` (estos reciben todos los permisos de gestión).

## USUARIO-017

El design system del proyecto se sirve en `/design-system/` y requiere el permiso `gestion.ver_design_system`. El enlace "Design system" aparece en el menú de usuario solo cuando la persona tiene ese permiso. Este permiso está separado de `gestion.ver_especificacion`: una cosa es leer la especificación funcional y otra consultar la referencia visual para construir pantallas.
