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

El grupo `Atención al asociado` representa a quienes realizan la operación
diaria. Puede abrir gestión, consultar y editar datos ordinarios de asociados y
cobrar cuotas. No puede dar de baja, importar, exportar, consultar deudores,
administrar períodos ni ver la auditoría general. En la carga inicial, el
usuario `atencion` también queda vinculado a un asociado de prueba para probar
el selector de paneles.

## USUARIO-011

Los grupos son acumulables. Una persona puede pertenecer a más de un área sin
crear un grupo combinado. La migración de roles crea los grupos operativos
`Atención al asociado`, `Administrador de permisos`, `Gestión de convenios`,
`Gestión de publicidades`, `Administrador de la mutual` y `Administrador de la
app`, además de los grupos de experiencia `Asociados` y `Comercios`.

## USUARIO-012

`create_user_for_comercio(comercio, password)` en `usuarios/services.py` crea un usuario Django, lo vincula al comercio y lo asigna al grupo `Comercios`. El username se genera como `com-{id}`. Rechaza con `ValueError` si el comercio ya tiene usuario.

## USUARIO-013

`GestionCrearUsuarioAsociadoView` en `gestion/views.py` permite a un usuario con permiso `editar_asociados` crear un usuario para un asociado desde la pantalla de detalle. Usa el DNI como username por defecto. Redirige al detalle con mensaje de éxito o error. GET redirige sin acción.

## USUARIO-014

`GestionCrearUsuariosAsociadosFaltantesView` en `gestion/views.py` permite a un usuario con permiso `importar_asociados` crear usuarios para los asociados sin usuario vinculado desde la pantalla de importación de padrón. Usa el DNI como username y contraseña inicial. Si ya existe un usuario con username igual al DNI y no está vinculado a otro asociado, lo vincula al asociado. Si un asociado falla, registra el error y sigue con los demás. La acción se ejecuta por tandas para evitar timeouts de Vercel y puede repetirse hasta completar el padrón. El comportamiento sigue siendo idempotente: si se ejecuta otra vez, no duplica usuarios ya vinculados.

## USUARIO-015

El `GestionPermissionRequiredMixin` usa `UserPassesTestMixin` con `raise_exception = True` para rechazar con 403 en lugar de redirigir al login. Las vistas deben declarar su lógica en métodos `get()`/`post()` y no en `dispatch()` para que el permiso se evalúe antes.

## USUARIO-016

La especificación del proyecto se sirve en `/especificacion/` y requiere el
permiso `gestion.ver_especificacion`. Usa un mixin propio
`VerEspecificacionRequiredMixin`. El permiso se asigna al `Administrador de la
mutual`; el superusuario técnico también lo obtiene por su condición de
superusuario.

## USUARIO-017

El design system del proyecto se sirve en `/design-system/` y requiere el permiso `gestion.ver_design_system`. El enlace "Design system" aparece en el menú de usuario solo cuando la persona tiene ese permiso. Este permiso está separado de `gestion.ver_especificacion`: una cosa es leer la especificación funcional y otra consultar la referencia visual para construir pantallas.

## USUARIO-018 — Inicio inteligente

La raíz del sitio (`/`) funciona como inicio inteligente: en lugar de servir siempre la home pública, evalúa la sesión actual y redirige al destino más útil.

| Situación | Destino |
|---|---|
| Visitante sin sesión | Home pública (`web:home`) |
| Usuario autenticado con 1 experiencia (asociado, gestión o comercio) | Home de esa experiencia |
| Usuario autenticado con 2+ experiencias | Pantalla Elegir panel |
| Usuario autenticado sin ninguna experiencia (solo tiene usuario pero sin vínculos) | Home pública (`web:home`) |

Las experiencias se determinan así:
- **Asociado**: el usuario tiene un `Asociado` vinculado y pertenece al grupo `Asociados`.
- **Gestión**: el usuario tiene el permiso `gestion.ver_dashboard_gestion`.
- **Comercio**: el usuario tiene un `Comercio` vinculado y pertenece al grupo `Comercios`.

El logo de la aplicación (arriba a la izquierda) enlaza a `/`, respetando el mismo criterio de inicio inteligente.

El enlace "Sitio público" está disponible en el menú de usuario autenticado para acceder a la home pública en cualquier momento.

En el MVP el sistema no recuerda el último panel elegido. Cada visita a `/` o al logo vuelve a evaluar las experiencias disponibles.

## USUARIO-019 — Matriz inicial de grupos

| Grupo | Gestión propia | Admin técnico | Exclusiones principales |
|---|---|---|---|
| Atención al asociado | Consulta y edición ordinaria de asociados; cobros | No requerido | Baja, importaciones, exportación, deudores, períodos y auditoría general |
| Administrador de permisos | Dashboard y auditoría | Alta, consulta y edición de usuarios; consulta de grupos | No modifica la definición de grupos, no edita superusuarios ni puede asignar `Administrador de la app` |
| Gestión de convenios | Dashboard | Actividades comerciales y comercios | Usuarios, asociados, publicidades y auditoría general |
| Gestión de publicidades | Dashboard | Categorías, productos/servicios y publicidades; consulta comercios para vincular | Modificación de comercios, usuarios, asociados y auditoría general |
| Administrador de la mutual | Toda la operación regular, reportes y auditoría | Dominios de asociados, cuotas, convenios y contenidos; finanzas en solo lectura; usuarios en consulta | Importaciones masivas, permisos técnicos, superusuarios y borrados |
| Administrador de la app | Todos los accesos por `is_superuser` | Administración técnica completa con las restricciones de integridad del sistema | No es un rol operativo delegable |

## USUARIO-020 — `is_staff`, grupos y superusuario

Los permisos de un grupo y `is_staff` cumplen funciones diferentes. Los grupos
determinan qué puede hacer la persona; `is_staff=True` permite entrar al admin
de Django. Al guardar un usuario, Uni2 sincroniza automáticamente `is_staff`
según el permiso `usuarios.acceder_admin_tecnico`. Al retirar la última
asignación de esa capacidad, retira `is_staff`, salvo que la cuenta sea
superusuario.

La lógica no contiene nombres de grupos. Los grupos iniciales Administrador de
permisos, Gestión de convenios, Gestión de publicidades y Administrador de la
mutual reciben la capacidad en la migración inicial. Un grupo futuro puede
habilitar el admin recibiendo el mismo permiso, sin cambiar código Python.

La sincronización vive en `usuarios.services.sincronizar_acceso_admin()` y se
ejecuta desde el admin después de guardar la relación de grupos. No usa signals.
La migración inicial corrige también usuarios que ya pertenecían a los roles
iniciales alcanzados.

`Administrador de la app` es una etiqueta organizativa para cuentas con
`is_superuser=True`; pertenecer al grupo no concede permisos. Sólo otro
superusuario puede crear o modificar una cuenta de ese nivel. El admin delegado
de usuarios oculta `is_superuser`, permisos individuales y el grupo
`Administrador de la app`, y rechaza la edición de superusuarios.

## USUARIO-021 — Importaciones masivas

Los permisos `gestion.importar_asociados` y
`gestion.importar_cuotas_historicas`, incluida la creación masiva de usuarios
faltantes asociada al padrón, no se asignan a ningún grupo operativo. Se
reservan al `Administrador de la app`, que los obtiene por `is_superuser`. La
exportación regular de asociados sí pertenece al Administrador de la mutual.
