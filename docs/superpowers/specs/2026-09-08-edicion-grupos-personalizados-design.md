# Edición delegada de grupos

## Contexto

La mutual administra sus grupos desde el admin de Django. En la implementación
actual, `Uni2GroupAdmin` agrega restricciones propias sobre la autorización
estándar. Esto puede volver inefectivo el permiso `auth.change_group` asignado
explícitamente a una persona.

## Comportamiento acordado

Una persona con el permiso efectivo `auth.change_group` puede editar cualquier
grupo desde el admin de Django. La autorización usa exclusivamente el mecanismo
estándar de permisos de Django: no depende del nombre del grupo que se intenta
modificar, del grupo al que pertenece la persona ni de una lista adicional de
grupos protegidos.

## Alcance de implementación

Se eliminará la personalización de
`Uni2GroupAdmin.has_change_permission`. `GroupAdmin` resolverá la edición con
el permiso estándar `auth.change_group`, sin una segunda capa de autorización.

No se modificarán el alta ni el borrado de grupos. El alta continuará reservada
al superusuario y el borrado continuará deshabilitado.

## Pruebas

Las pruebas del admin verificarán que:

- un usuario no superusuario con `auth.change_group` puede editar un grupo
  personalizado y también los grupos existentes de Uni2;
- un usuario sin `auth.change_group` no puede editar grupos;
- el superusuario conserva la edición de todos los grupos.

## Documentación funcional

La especificación de usuarios indicará que los grupos son administrados por la
mutual y que `auth.change_group` habilita la edición de cualquiera de ellos, sin
excepciones adicionales.

## Fuera de alcance

- Crear una pantalla propia de gestión de grupos.
- Incorporar listas de permisos permitidos o prohibidos.
- Cambiar el alta o el borrado de grupos.
- Reorganizar la matriz histórica de grupos en este cambio.
