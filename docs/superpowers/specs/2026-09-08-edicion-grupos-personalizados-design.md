# Edición delegada de grupos personalizados

## Contexto

La mutual administra sus grupos personalizados desde el admin de Django. En la
implementación actual, `Uni2GroupAdmin` rechaza toda edición realizada por una
persona que no sea superusuario, incluso cuando Django le reconoce el permiso
`auth.change_group`. Esto vuelve inefectivo un permiso asignado explícitamente.

## Comportamiento acordado

Una persona con el permiso efectivo `auth.change_group` puede editar grupos
personalizados desde el admin de Django. La autorización usa el mecanismo
estándar de permisos de Django; no depende del nombre del grupo al que pertenece
la persona.

Los siguientes grupos técnicos permanecen protegidos y solo pueden ser editados
por un superusuario:

- `Administrador de la app`;
- `Asociados`;
- `Comercios`.

La protección se evalúa sobre el grupo que se intenta modificar. Un usuario con
`auth.change_group` puede entrar al listado y editar cualquier otro grupo.

## Alcance de implementación

Se modificará únicamente `Uni2GroupAdmin.has_change_permission` para:

1. conservar la decisión estándar de Django para grupos personalizados;
2. rechazar la edición de los tres grupos técnicos cuando el usuario no sea
   superusuario.

No se modificarán el alta ni el borrado de grupos. El alta continuará reservada
al superusuario y el borrado continuará deshabilitado.

## Pruebas

Las pruebas del admin verificarán que:

- un usuario no superusuario con `auth.change_group` puede editar un grupo
  personalizado;
- el mismo usuario no puede editar `Administrador de la app`, `Asociados` ni
  `Comercios`;
- un usuario sin `auth.change_group` no puede editar grupos personalizados;
- el superusuario conserva la edición de todos los grupos.

## Documentación funcional

La especificación de usuarios indicará que los permisos de los grupos
personalizados son administrados por la mutual y que `auth.change_group`
habilita su edición. También dejará explícita la protección de los tres grupos
técnicos.

## Fuera de alcance

- Crear una pantalla propia de gestión de grupos.
- Incorporar listas de permisos permitidos o prohibidos.
- Cambiar el alta o el borrado de grupos.
- Reorganizar la matriz histórica de grupos en este cambio.
