# Borrado excepcional de períodos de cuota desde el admin

## Objetivo

Ampliar la limpieza excepcional de la carga inicial para que un superusuario
pueda borrar períodos de cuota desde el admin técnico de Django.

## Permisos

- `PeriodoCuotaAdmin` habilita expresamente el borrado reservado a
  `is_superuser=True`.
- La excepción comprende el borrado individual y la acción masiva
  `Eliminar seleccionados`.
- Los usuarios delegados no pueden borrar períodos aunque tengan permisos para
  administrarlos.
- `Cuota`, `Pago`, `PagoCuota` y `Donacion` mantienen bloqueado su borrado
  directo desde el admin.

## Integridad

La relación `Cuota.periodo` conserva `on_delete=PROTECT`. Por lo tanto, Django
impide borrar un período mientras existan cuotas que lo referencien. La
limpieza debe eliminar primero los asociados y sus cuotas relacionadas.

No se modifica el modelo y no se genera una migración.

## Auditoría

Como en el resto de la limpieza inicial aprobada, la eliminación no genera un
`EventoAuditoria` de Uni2. Django conserva su registro técnico estándar del
admin.

## Pruebas y documentación

Las pruebas verificarán que solamente el superusuario ve y ejecuta las acciones
de borrado de `PeriodoCuota`, que un período sin cuotas puede eliminarse y que
`PROTECT` rechaza la eliminación cuando existen cuotas relacionadas.

La especificación OKF documentará el permiso excepcional y la restricción de
integridad.
