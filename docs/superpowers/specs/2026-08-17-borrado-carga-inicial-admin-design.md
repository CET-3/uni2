# Borrado excepcional de la carga inicial desde el admin

## Objetivo

Permitir que un superusuario limpie datos de la carga inicial desde el admin
técnico de Django en desarrollo, staging y producción.

La capacidad se limita a cursos, asociados y usuarios. No se habilita el
borrado general para los demás modelos que usan `AuditoriaAdminMixin`.

## Permisos

- Solo una cuenta con `is_superuser=True` puede borrar `Curso`, `Asociado` o
  `User` desde el admin.
- La habilitación comprende el borrado individual y la acción masiva
  `Eliminar seleccionados`.
- Un usuario delegado conserva denegado el borrado aunque tenga permisos
  Django sobre el modelo.
- El bloqueo predeterminado de `AuditoriaAdminMixin` se mantiene. Cada uno de
  los tres administradores permitidos declara explícitamente la excepción.

## Comportamiento y relaciones

Antes de confirmar, Django muestra su pantalla habitual con los objetos
relacionados que resultarán afectados.

- Al borrar un asociado se eliminan en cascada sus cuotas, pagos, aplicaciones
  de pagos y donaciones.
- Al borrar un curso, `curso_actual` queda vacío en los asociados que lo
  usaban.
- Al borrar un usuario, el asociado vinculado queda sin usuario.

No se agregan eventos de eliminación a `EventoAuditoria`, porque esta capacidad
se usará de manera excepcional para depurar la carga inicial. Se conserva el
registro técnico estándar que genera el admin de Django.

## Implementación

`AuditoriaAdminMixin` ofrecerá una opción explícita, desactivada por defecto,
para permitir borrado a superusuarios. `CursoAdmin`, `AsociadoAdmin` y
`Uni2UserAdmin` activarán esa opción.

El permiso efectivo combinará ambas condiciones:

1. el administrador del modelo habilitó expresamente la excepción;
2. la persona autenticada es superusuario y Django le concede el permiso de
   borrado correspondiente.

## Pruebas

Las pruebas verificarán que:

- un superusuario puede borrar cursos, asociados y usuarios;
- un usuario no superusuario no puede hacerlo;
- otro modelo que hereda `AuditoriaAdminMixin` continúa sin borrado;
- la acción masiva aparece solamente para los tres modelos habilitados;
- las relaciones siguen las reglas de cascada o `SET_NULL` definidas por los
  modelos.

## Documentación funcional

La especificación indicará que el admin técnico permite al Administrador de la
app eliminar cursos, asociados y usuarios como limpieza excepcional de la
carga inicial. También dejará explícito que no es el flujo ordinario de baja de
asociados y que no genera un `EventoAuditoria` de Uni2.
