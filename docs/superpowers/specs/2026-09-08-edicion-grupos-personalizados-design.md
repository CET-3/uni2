# Edición delegada de grupos

## Contexto

La mutual administra sus grupos desde el admin de Django. En la implementación
actual, `Uni2GroupAdmin` agrega restricciones propias sobre la autorización
estándar. Esto puede volver inefectivo el permiso `auth.change_group` asignado
explícitamente a una persona.

## Comportamiento acordado

Una persona con los permisos efectivos `auth.add_group`, `auth.change_group` o
`auth.delete_group` puede respectivamente crear, editar o borrar grupos desde
el admin de Django. La autorización usa exclusivamente el mecanismo estándar de
permisos de Django: no depende del nombre del grupo que se intenta modificar,
del grupo al que pertenece la persona ni de una lista adicional de grupos
protegidos.

## Alcance de implementación

Se eliminarán las restricciones de `Uni2GroupAdmin` para el alta y la edición,
de modo que herede directamente esas decisiones de `GroupAdmin`. Para el
borrado, `Uni2GroupAdmin.has_delete_permission` delegará explícitamente en
`GroupAdmin`: así conserva `AuditoriaAdminMixin` para los cambios, pero no aplica
su bloqueo general de borrado. Las tres operaciones se resolverán mediante los
permisos estándar correspondientes.

## Pruebas

Las pruebas del admin verificarán que:

- un usuario no superusuario con `auth.add_group` puede crear grupos;
- un usuario no superusuario con `auth.change_group` puede editar un grupo
  personalizado y también los grupos existentes de Uni2;
- un usuario no superusuario con `auth.delete_group` puede borrar grupos;
- un usuario sin `auth.change_group` no puede editar grupos;
- el superusuario conserva la edición de todos los grupos.

## Documentación funcional

La especificación de usuarios indicará que los grupos son administrados por la
mutual y que `auth.add_group`, `auth.change_group` y `auth.delete_group`
habilitan el alta, la edición y el borrado respectivamente, sin excepciones
adicionales.

## Fuera de alcance

- Crear una pantalla propia de gestión de grupos.
- Incorporar listas de permisos permitidos o prohibidos.
- Reorganizar la matriz histórica de grupos en este cambio.
