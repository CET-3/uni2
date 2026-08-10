# Plan: navegación pública por secciones y breadcrumbs consistentes

## Estado

Implementado sobre `feature/home-atencion-asociado` como parte del PR de navegación.

Este documento conserva las decisiones que guiaron la implementación. La especificación OKF fue actualizada en el mismo trabajo y vuelve a ser la fuente de verdad del comportamiento vigente.

## Dependencias y orden

- Depende de `plan-home-unica.md`.
- Debe implementarse después de la home única, porque los enlaces con fragmentos deben apuntar siempre a `/` y encontrar allí las secciones públicas, incluso con una sesión iniciada.
- No depende de `plan-navegacion-atencion-asociado.md`; ambos pueden implementarse en paralelo después de completar la home única.
- No se deben introducir enlaces temporales a `/inicio/`, porque esa ruta será retirada por el plan base.

## Objetivo

Usar la home como punto central para consultar productos, servicios y comercios, evitando que la navegación principal lleve a páginas de listado que duplican ese contenido.

También se unificará el criterio de los breadcrumbs de las páginas públicas: no incluirán `Inicio`, porque el logo ya cumple la función de volver a la home, y mostrarán siempre una jerarquía consistente hasta la página actual.

## 1. Navegación principal

Cambiar los enlaces de la navbar:

- `Productos y servicios` debe llevar a la sección correspondiente de la home.
- `Comercios` debe llevar a la sección de beneficios y comercios de la home.
- La navegación principal dejará de dirigir a las páginas independientes de listado.

Usar estas anclas estables:

- `/#productos-servicios`
- `/#beneficios`

Agregar `id="productos-servicios"` a la sección compartida de servicios. Conservar `beneficios`, que ya existe como identificador de la sección de comercios.

Como la home única ya estará implementada:

- El destino será `web:home` más el fragmento correspondiente.
- Todas las variantes autenticadas de la home contendrán las secciones públicas.
- No será necesario conservar enlaces temporales a `/inicio/`.

Las páginas de listado podrán conservarse por compatibilidad, pero dejarán de formar parte de la navegación principal.

## 2. Comportamiento mobile de las anclas

- Al seleccionar `Productos y servicios` o `Comercios` desde el menú mobile, cerrar automáticamente el menú desplegado.
- Realizar el desplazamiento hasta la sección después de cerrar el menú, para que el cambio de altura no altere la posición final.
- Aplicar margen de desplazamiento a las secciones para impedir que la navbar sticky tape sus títulos.
- Contemplar la altura adicional del banner de staging y los safe areas cuando la aplicación está instalada como PWA.
- No exigir desplazamiento animado y respetar `prefers-reduced-motion`.

Los títulos de las secciones deben:

- Poder ocupar más de una línea.
- Permanecer completamente visibles debajo de la navbar.
- No provocar desplazamiento horizontal.
- Mantener su jerarquía, alineación y separación en anchos de 320, 360 y 390 píxeles.

## 3. Convención de breadcrumbs

Eliminar `Inicio` de todos los breadcrumbs públicos.

Aplicar estas jerarquías:

- Categoría: `Productos y servicios > {categoría}`.
- Producto o servicio: `Productos y servicios > {categoría} > {producto o servicio}`.
- Actividad comercial: `Comercios > {actividad}`.
- Comercio disponible: `Comercios > {actividad} > {comercio}`.
- Comercio próximamente disponible: `Comercios > {actividad} > {comercio}`.

Reglas comunes:

- `Productos y servicios` enlaza a `/#productos-servicios`.
- `Comercios` enlaza a `/#beneficios`.
- La categoría o actividad intermedia enlaza a su página de detalle.
- El último elemento representa la página actual, no tiene enlace y usa `aria-current="page"`.
- Los nombres largos pueden envolver correctamente en mobile.
- Ningún breadcrumb incluye `Inicio`.

## 4. Componente compartido

Simplificar la interfaz del componente de breadcrumbs:

- Eliminar el comportamiento implícito que agrega `Inicio` por defecto.
- Reemplazar parámetros especiales como `hide_home` y `current_url` por niveles explícitos:
  - Raíz de sección.
  - Ancestro intermedio opcional.
  - Página actual.
- Mantener una lista ordenada semántica dentro de un `nav` con nombre accesible.
- Actualizar el ejemplo del design system para mostrar la nueva convención sin `Inicio`.

## 5. Enlaces secundarios de los detalles

Para evitar que otros botones contradigan la nueva navegación:

- Cambiar `Todos los productos` para que vuelva a `/#productos-servicios`.
- Cambiar `Todos los comercios` para que vuelva a `/#beneficios`.
- Revisar cualquier otro enlace público que todavía dirija a los listados completos.
- No eliminar todavía las rutas de listado; solamente retirar su uso dentro del recorrido principal.

## 6. Pruebas previstas

- Los enlaces `Productos y servicios` y `Comercios` de la navbar contienen los fragmentos correctos.
- Los enlaces principales ya no apuntan a `web:productos_servicios` ni `web:comercios`.
- Las secciones objetivo existen en la home.
- El menú mobile se cierra al elegir una sección.
- Los títulos quedan visibles debajo de la navbar en mobile y en staging.
- No existe desbordamiento horizontal en anchos pequeños.
- Ningún breadcrumb público contiene `Inicio`.
- Todos los breadcrumbs incluyen la página actual con `aria-current="page"`.
- Los detalles de producto y comercio muestran correctamente sus tres niveles.
- Los enlaces `Todos los productos` y `Todos los comercios` vuelven a la sección correspondiente de la home.
- Las rutas independientes de listado continúan funcionando mientras se conserven por compatibilidad.

## 7. Actualización de la especificación

Al implementar, actualizar:

- La pantalla del sitio público.
- La navegación global.
- La documentación del componente breadcrumb en el design system.
- Los casos de uso públicos que todavía describan las páginas de listado como entrada principal.
