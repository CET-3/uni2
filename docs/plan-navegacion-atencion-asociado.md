# Plan: simplificar la navegación de atención al asociado

## Estado

Implementado sobre la rama `staging` en el mismo trabajo que la home única.

Este documento conserva las decisiones que guiaron la implementación. La especificación OKF fue actualizada en el mismo trabajo y vuelve a ser la fuente de verdad del comportamiento vigente.

**Ajuste posterior:** la auditoría ya no aparece como botón en el encabezado, pero se incorporó al pie del detalle como historial contextual. `gestion.ver_movimientos_asociado` habilita las diez operaciones más recientes y `gestion.ver_auditoria` mantiene, de forma separada, la consulta completa y su enlace. El grupo Atención al asociado recibe solo el primer permiso.

## Dependencias y orden

- Depende de `plan-home-unica.md`.
- Debe implementarse después de la home única, porque el acceso `Atención al asociado` vivirá en el hero administrativo y el dashboard de gestión ya no existirá.
- No depende de `plan-navegacion-publica-breadcrumbs.md`; ambos pueden implementarse en paralelo después de completar la home única.
- No se deben hacer primero cambios temporales sobre los CTA del dashboard actual: se aplicará directamente el resultado final sobre la home unificada.

## Objetivo

Simplificar el recorrido cotidiano de gestión de asociados para que tenga una dirección clara:

`Atención al asociado → detalle → cobrar o editar → detalle`

La consulta será el punto de entrada para buscar o crear asociados. El detalle será el centro operativo desde el cual se podrá cobrar o editar. Tanto la cancelación como la finalización exitosa de esas acciones volverán al detalle.

## 1. Entrada a la funcionalidad

- Renombrar el CTA que abre la consulta como `Atención al asociado`.
- Eliminar el CTA contiguo actual.
- No agregar todavía el acceso a consulta de cuotas.
- Aplicar este criterio directamente al hero administrativo de la home única.
- Renombrar la card o acceso duplicado de `Asociados` para que toda la navegación use consistentemente `Atención al asociado`.

## 2. Consulta de asociados

- Mantener la búsqueda, los filtros y los resultados actuales.
- Convertir cada fila completa en un acceso al detalle del asociado.
- Usar un único enlace accesible dentro de cada fila y ampliar visualmente su área interactiva. Evitar crear un enlace separado en cada celda.
- Agregar estados visuales de hover y foco para dejar claro que la fila es seleccionable con mouse o teclado.
- Eliminar la columna de acciones.
- Eliminar los botones `Ver detalle` y `Cobrar`.
- Conservar `Nuevo asociado` y `Exportar asociados`, sujetos a sus permisos actuales.
- No incluir `Volver al panel`, porque la navegación global cumple esa función y el dashboard ya habrá sido retirado por el plan de home única.
- Retirar `Importar padrón inicial` de esta pantalla, porque es una tarea de puesta en marcha y no de atención cotidiana.

## 3. Detalle del asociado

El encabezado tendrá únicamente estas acciones operativas:

- `Cobrar`, si el usuario posee `gestion.cobrar_cuotas`.
- `Editar asociado`, si el usuario posee `gestion.editar_asociados`.

Retirar del encabezado:

- `Ver todas las cuotas`.
- `Ver auditoría`.
- `Crear usuario`.
- El botón `Volver al listado`.

Para no dejar al usuario encerrado, reemplazar el botón de regreso por una navegación secundaria que no se presente como acción, por ejemplo:

`Atención al asociado / Apellido, Nombre`

El primer nivel volverá al listado. Cuando el detalle se haya abierto desde una búsqueda, debe conservar sus filtros mediante un parámetro de retorno validado. Si no existe un retorno válido, usará el listado sin filtros.

La información actual del detalle —datos, deuda, cuotas del año y pagos recientes— permanecerá sin cambios.

## 4. Edición

- Mantener `Guardar cambios` y `Cancelar`.
- Eliminar el botón duplicado `Volver al detalle` del encabezado.
- Renombrar el acceso del detalle de `Editar datos` a `Editar asociado`.
- Hacer que `Cancelar` vuelva siempre al detalle del asociado.
- Después de una edición exitosa, mostrar el mensaje de confirmación y volver al mismo detalle.
- Si el formulario contiene errores, permanecer en edición y conservar los datos ingresados.
- Preservar en el detalle el contexto necesario para regresar posteriormente al listado filtrado.

La redirección exitosa de edición ya termina actualmente en el detalle; debe conservarse y cubrirse explícitamente con pruebas.

## 5. Cobro

- Iniciar el cobro exclusivamente desde el detalle del asociado.
- Eliminar del encabezado de cobro los accesos `Buscar asociado` y `Volver al panel`.
- Eliminar el botón `Ver detalle` del resumen del asociado.
- Mantener los datos identificatorios del asociado, sin acciones adicionales.
- Colocar `Cancelar` junto a `Confirmar cobro`.
- Hacer que `Cancelar` vuelva al detalle sin registrar cambios.
- Después de un cobro exitoso, mostrar el mensaje correspondiente y volver al detalle.
- Si el cobro contiene errores, permanecer en el formulario y conservar el asociado, las cuotas seleccionadas y los datos ingresados.
- Si se abre `/gestion/cobros/` sin asociado seleccionado, redirigir a `Atención al asociado` con un mensaje orientativo en lugar de mostrar una pantalla intermedia.

## 6. Alta de asociado

Actualmente, si el operador tiene permiso para cobrar, un alta exitosa salta directamente al cobro. Eso rompe el nuevo recorrido centrado en el detalle.

Cambiar el comportamiento para que:

- Toda alta exitosa termine siempre en el detalle del asociado creado.
- El detalle muestre el mensaje de éxito y la cantidad de cuotas iniciales generadas.
- Desde allí el operador decida explícitamente si quiere cobrar o editar.
- `Cancelar` en el alta continúe volviendo a `Atención al asociado`.

## 7. Funcionalidades que dejan de tener acceso principal

Este cambio retira del detalle tres accesos existentes:

- Historial completo de cuotas.
- Auditoría filtrada por asociado.
- Creación individual de usuario.

Por ahora se conservarán sus vistas, rutas y permisos para no eliminar funcionalidad mientras se diseñan los nuevos recorridos:

- La auditoría general continúa disponible desde su acceso administrativo.
- La creación masiva de usuarios continúa disponible desde la importación.
- La vista histórica de cuotas queda sin acceso principal hasta diseñar la consulta de cuotas.

Esta situación debe documentarse como una decisión temporal. Cuando se diseñen esos recorridos habrá que decidir si las rutas actuales se reutilizan o se retiran.

## 8. Pruebas previstas

- El acceso principal se llama `Atención al asociado` y no tiene un segundo CTA contiguo.
- La consulta conserva búsqueda, filtros, alta y exportación según permisos.
- Cada fila de resultados es navegable completa y accesible por teclado.
- La tabla no contiene columna de acciones ni botones `Ver detalle` o `Cobrar`.
- El detalle muestra únicamente `Cobrar` y `Editar asociado`, sujetos a permisos.
- La navegación secundaria permite volver al listado y conserva los filtros cuando corresponde.
- Cancelar o completar correctamente una edición vuelve al detalle.
- Cancelar o completar correctamente un cobro vuelve al detalle.
- Los formularios inválidos permanecen en su pantalla y conservan sus datos.
- Abrir cobros sin asociado redirige a `Atención al asociado`.
- Toda alta exitosa redirige al detalle, independientemente del permiso de cobro.
- Los botones y accesos retirados dejan de aparecer en las pantallas.

## 9. Actualización de la especificación

Al implementar, actualizar:

- La pantalla de gestión y su navegación.
- El caso de uso de consulta de asociados.
- El caso de uso de detalle de asociado.
- El caso de uso de alta de asociado.
- El caso de uso de edición de asociado.
- El caso de uso de registro de pago.
- La documentación de cuotas, auditoría y creación de usuario para dejar asentado que sus accesos desde el detalle fueron retirados temporalmente.
