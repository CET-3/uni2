---
type: "Regla de negocio"
title: "Usuarios"
description: "Reglas de negocio sobre usuarios."
tags: [mvp, reglas]
timestamp: 2026-06-22T00:00:00-03:00
---

# Usuarios

## USUARIO-001

El alta individual de un asociado crea automáticamente un usuario vinculado.
Esto comprende el alta manual desde Gestión y la finalización de una
preinscripción. La importación inicial del padrón, las escrituras desde el admin
técnico o el ORM y otros procesos masivos no crean ni notifican usuarios de
forma implícita.

## USUARIO-002

El administrador puede crear un usuario para un asociado existente.

## USUARIO-003

No se puede crear un nuevo usuario para un asociado que ya tiene uno vinculado.

## USUARIO-004

El username y la contraseña inicial del asociado son su DNI. Si el alta
individual tiene email, el sistema envía una comunicación `alta_usuario`. Si no
tiene email, la cuenta se crea igualmente sin intentar el envío.

## USUARIO-005

El listado de asociados debe mostrar si tiene usuario y el ultimo acceso usando `User.last_login`.

## USUARIO-006

En el admin técnico de Django, el listado de usuarios debe mostrar los grupos asignados para facilitar la operación de roles.

## USUARIO-007

La experiencia de asociado se habilita por vínculo con `Asociado`, la de comercio por vínculo con `Comercio` y la administrativa por permisos operativos de la app `gestion`. Las tres experiencias comparten la misma home y cambian solamente la presentación y los accesos del hero.

## USUARIO-008

Si un usuario tiene más de una experiencia disponible, luego del login ve en la home el hero `Elegí cómo querés ingresar`. Puede elegir asociado, comercio o administración mediante `?perfil=` sin salir de la home.

## USUARIO-009

El acceso al admin técnico requiere una cuenta activa con al menos un permiso
efectivo sobre un modelo registrado, o una cuenta superusuario. `is_staff` no
define este acceso ni qué tareas operativas puede usar una persona en
`gestion`. Las pantallas y acciones se controlan con permisos Django propios de
cada app.

## USUARIO-010

El grupo `Atención al asociado` representa a quienes realizan la operación
diaria. Puede abrir gestión, consultar y editar datos ordinarios de asociados,
gestionar solicitudes de asociación —incluida su cancelación y el reenvío de
sus comunicaciones— y cobrar cuotas.
No puede dar de baja asociados, importar, exportar, consultar deudores,
administrar períodos ni ver la auditoría general. En la carga inicial, el
usuario `atencion` también queda vinculado a un asociado de prueba para probar
la variante multiperfil de la home.

## USUARIO-011

Los grupos son acumulables. Una persona puede pertenecer a más de un área sin
crear un grupo combinado. La migración de roles crea los grupos operativos
`Atención al asociado`, `Administrador de permisos`, `Gestión de convenios`,
`Gestión de productos y servicios`, `Gestión de publicidades`, `Administrador
de la mutual`, `Equipo del proyecto` y `Administrador de la app`, además de los
grupos de experiencia `Asociados` y `Comercios`.

## USUARIO-012

`create_user_for_comercio(comercio, password)` en `usuarios/services.py` crea un usuario Django, lo vincula al comercio y lo asigna al grupo `Comercios`. El username se genera como `com-{id}`. Rechaza con `ValueError` si el comercio ya tiene usuario.

## USUARIO-013

`GestionCrearUsuarioAsociadoView` en `gestion/views.py` permite a un usuario con permiso `editar_asociados` crear un usuario para un asociado desde la pantalla de detalle. Usa el DNI como username por defecto. Redirige al detalle con mensaje de éxito o error. GET redirige sin acción.

## USUARIO-014

`GestionCrearUsuariosAsociadosFaltantesView` en `gestion/views.py` permite a un usuario con permiso `importar_asociados` crear usuarios para los asociados sin usuario vinculado desde la pantalla de importación de padrón. Usa el DNI como username y contraseña inicial. Si ya existe un usuario con username igual al DNI y no está vinculado a otro asociado, lo vincula al asociado. Si un asociado falla, registra el error y sigue con los demás. La acción se ejecuta por tandas para evitar timeouts de Vercel y puede repetirse hasta completar el padrón. El comportamiento sigue siendo idempotente: si se ejecuta otra vez, no duplica usuarios ya vinculados. Esta acción masiva nunca envía correos de alta.

## USUARIO-015

El `GestionPermissionRequiredMixin` usa `UserPassesTestMixin` con `raise_exception = True` para rechazar con 403 en lugar de redirigir al login. Las vistas deben declarar su lógica en métodos `get()`/`post()` y no en `dispatch()` para que el permiso se evalúe antes.

## USUARIO-016

La especificación del proyecto se sirve en `/especificacion/` y requiere el
permiso `gestion.ver_especificacion`. Usa un mixin propio
`VerEspecificacionRequiredMixin`. El permiso se asigna a `Equipo del proyecto`;
el superusuario técnico también lo obtiene por su condición de superusuario.

## USUARIO-017

El design system del proyecto se sirve en `/design-system/` y requiere el permiso `gestion.ver_design_system`. El enlace "Design system" aparece en el menú de usuario solo cuando la persona tiene ese permiso. Este permiso está separado de `gestion.ver_especificacion`: una cosa es leer la especificación funcional y otra consultar la referencia visual para construir pantallas.

## USUARIO-018 — Home única por experiencia

La raíz del sitio (`/`) siempre renderiza la misma home. No redirige a dashboards ni a una pantalla selectora. La sesión actual determina solamente el contenido del hero; las secciones públicas de servicios, beneficios, publicidades y asociación permanecen debajo para todas las variantes.

| Situación | Hero |
|---|---|
| Visitante sin sesión | Presentación pública con `Sumate` e `Iniciar sesión` |
| Usuario autenticado con una experiencia | Presentación y hasta dos CTA de esa experiencia |
| Usuario autenticado con dos o más experiencias, sin `perfil` válido | `Elegí cómo querés ingresar` y hasta dos accesos de perfil |
| Usuario multiperfil con `?perfil=asociado`, `comercio` o `gestion` autorizado | Presentación de la experiencia elegida |
| Usuario autenticado sin experiencias | Presentación pública sin CTA de login |

Las experiencias se determinan así:

- **Asociado**: existe un `Asociado` vinculado al usuario.
- **Comercio**: existe un `Comercio` vinculado al usuario.
- **Administración**: el usuario tiene al menos un permiso operativo de la app `gestion`.

El hero admite como máximo dos CTA. Los perfiles o acciones autorizadas restantes se muestran en `Más accesos`, inmediatamente debajo del hero. La selección solicitada por `?perfil=` se acepta solamente si pertenece a las experiencias disponibles; un valor ausente, inválido o no autorizado vuelve al selector multiperfil.

El logo y el resultado exitoso del login enlazan a `/`. La selección no se guarda en sesión: cada visita a `/` sin parámetro vuelve a evaluar las experiencias. Ya no existen `/inicio/`, `/paneles/`, `/asociado/panel/`, `/comercio/panel/` ni `/gestion/`, y el menú no necesita un acceso separado llamado `Sitio público`.

## USUARIO-019 — Matriz inicial de grupos

| Grupo | Gestión propia | Admin técnico | Exclusiones principales |
|---|---|---|---|
| Atención al asociado | Consulta y edición ordinaria de asociados; solicitudes de asociación y reenvío de sus comunicaciones; cobros; últimos movimientos de la ficha | No requerido | Baja de asociados, importaciones, exportación, deudores, períodos y auditoría general |
| Administrador de permisos | Experiencia administrativa y auditoría | Alta, consulta y edición de usuarios; consulta de grupos | No edita superusuarios ni puede asignar `Administrador de la app` |
| Gestión de convenios | Experiencia administrativa | Actividades comerciales y comercios | Usuarios, asociados, publicidades y auditoría general |
| Gestión de productos y servicios | Experiencia administrativa | Categorías y productos/servicios | Publicidades, comercios, usuarios, asociados y auditoría general |
| Gestión de publicidades | Experiencia administrativa | Publicidades; consulta productos y comercios para vincular | Modificación de productos o comercios, usuarios, asociados y auditoría general |
| Administrador de la mutual | Toda la operación regular, reportes y auditoría | Dominios de asociados, cuotas, convenios y contenidos; finanzas en solo lectura; usuarios en consulta | Importaciones masivas, permisos técnicos, superusuarios y borrados |
| Equipo del proyecto | Especificación y design system | No requerido | Admin técnico, datos operativos y auditoría |
| Administrador de la app | Todos los accesos por `is_superuser` | Administración técnica completa con las restricciones de integridad del sistema | No es un rol operativo delegable |

## USUARIO-020 — Permisos y acceso al admin

Los grupos y permisos pueden ser definidos por cada mutual. Una cuenta activa
entra al admin si posee al menos un permiso efectivo (`view`, `add`, `change` o
`delete`) sobre un modelo registrado, o si es superusuario. Cada `ModelAdmin`
mantiene sus propias restricciones de acciones. `is_staff` puede conservarse
como dato técnico histórico, pero no es la fuente funcional de autorización.

Una cuenta con el permiso efectivo `auth.change_group` puede editar los grupos
personalizados definidos por la mutual. Los grupos técnicos `Administrador de
la app`, `Asociados` y `Comercios` solo pueden ser modificados por un
superusuario. Esta autorización no cambia las reglas de alta ni de borrado de
grupos.

La autorización se evalúa directamente contra los permisos efectivos de los
`ModelAdmin` registrados. La home y el menú muestran `Admin técnico` con la
misma regla, no por `is_staff`. Esto evita anunciar el admin a cuentas antiguas o ajustadas
manualmente que conservan la bandera técnica sin permisos de administración.

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

## USUARIO-022 — Configuración repetible de grupos

La matriz vigente de grupos y permisos se define una sola vez en
`usuarios/roles.py`. El comando `sincronizar_grupos` permite informar, aplicar o
verificar esa matriz en cualquier ambiente. Al aplicar reemplaza los permisos
de los grupos administrados por el conjunto exacto definido y alinea `is_staff`
por capacidad, pero no decide ni modifica sus integrantes.

Al separar `Gestión de productos y servicios` de `Gestión de publicidades`, la
migración agrega inicialmente al grupo nuevo a quienes ya integraban el grupo
histórico. Esto conserva accesos durante el despliegue; luego el Administrador
de permisos revisa cada responsabilidad y retira el grupo sobrante.

## USUARIO-023 — Acceso deducido a la administración

La experiencia `Administración` no tiene un permiso propio de dashboard. Se
ofrece cuando la persona posee al menos un permiso operativo real de `gestion`.
Cada pantalla mantiene su control específico y entrar al admin no autoriza
otras operaciones.

## USUARIO-024 — Borrado excepcional de la carga inicial

El Administrador de la app, identificado por `is_superuser=True`, puede borrar
`Curso`, `Asociado`, `PeriodoCuota` y `User` desde el admin técnico durante la
depuración de la carga inicial. La excepción incluye el borrado individual y la
acción masiva de Django. Los roles delegados no reciben esta capacidad aunque
tengan permisos de consulta o modificación sobre esas entidades.

Al borrar un usuario, el asociado vinculado queda sin usuario. Los demás
modelos administrados mantienen bloqueado el borrado directo. Un período que
tenga cuotas relacionadas conserva la protección de integridad y no puede
eliminarse.

## USUARIO-025 — Cambio de contraseña

Un asociado autenticado puede cambiar su contraseña indicando la contraseña
actual y confirmando la nueva. El cambio conserva su sesión actual y no envía
correo. Si no conoce la contraseña vigente debe usar el recorrido de
recuperación.

## USUARIO-026 — Recuperación de contraseña

La recuperación pública solicita DNI y email para identificar una cuenta
concreta aunque varias personas compartan una dirección. Solo genera el correo
`recuperacion_contrasena` cuando existe un asociado activo con usuario activo,
email no vacío y coincidencia de ambos datos.

Si DNI y email no corresponden a una cuenta activa y habilitada, el formulario
informa `No encontramos una cuenta activa con ese DNI y email. Revisá los datos
ingresados.` Esta respuesta explícita acepta que terceros puedan probar
combinaciones y confirmar la existencia de cuentas. Una cuenta encontrada
avanza a la confirmación. Cada cuenta admite un envío dentro de una ventana
configurable, inicialmente de 15 minutos; durante esa ventana sigue
considerándose encontrada, pero no genera otro correo. El enlace firmado vence
inicialmente después de una hora y se invalida al establecer una contraseña.

El email vigente de `Asociado` es la fuente de verdad. Los tokens y las
contraseñas no se persisten en comunicaciones, auditoría ni logs.

La solicitud bloquea primero el `Asociado` y después su `User`, y vuelve a
validar DNI, email, estados y vínculo antes de programar el correo. Así, una
edición simultánea de datos propios no puede enviar un enlace válido a una
dirección que dejó de pertenecer a la cuenta.

## USUARIO-027 — Sincronización de identidad y contacto

Cuando el asociado modifica sus propios nombre, apellido o email, el sistema
actualiza en la misma operación `User.first_name`, `User.last_name` o
`User.email`. El email puede quedar vacío; en ese caso deja de estar disponible
la recuperación por correo. Cargar un email después del alta no origina un
correo `alta_usuario` retroactivo.
