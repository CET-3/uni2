# Diseño: destinatarios e imágenes de productos y servicios

## Objetivo

Ampliar las fichas públicas de productos y servicios para que puedan:

- agrupar productos por ciclo y curso sin distinguir comisión ni turno;
- mostrar una foto propia de cada producto;
- mostrar una imagen informativa compartida por la categoría, acompañada por
  un título configurable;
- representar cuatro escenarios de precios con los dos campos existentes;
- abrir la ficha individual del producto al seleccionar su fila en la tabla de
  la categoría.

El diseño conserva la estructura pública actual de Uni2: breadcrumb, texto
introductorio a la izquierda y panel de precios a la derecha.

## Estado actual

`CategoriaProductoServicio` agrupa productos y contiene la descripción y el
texto de contacto. `ProductoServicio` contiene nombre, descripción, tipo,
precios, estado y orden.

La ficha de categoría muestra una tabla plana de productos activos. La ficha
individual muestra descripción y precios, pero no presenta fotos ni
destinatario escolar. Las filas de la categoría no enlazan actualmente a la
ficha individual.

## Destinatario escolar

`ProductoServicio` incorporará dos campos opcionales:

- `ciclo_destinatario`: ciclo escolar, con los valores usados por
  `Curso.division`, actualmente `CB` y `CS`;
- `curso_destinatario`: año del curso, con valores tomados de `Curso.anio`, por
  ejemplo `1ro` o `2do`.

Los campos guardan la combinación funcional y no una clave foránea a `Curso`.
Una relación directa sería incorrecta porque también ligaría el producto a una
comisión y un turno concretos. Distintos registros como `1ro 1ra CB TM` y
`1ro 2da CB TT` producen una sola combinación disponible: `1ro C.B.`.

El admin obtiene las combinaciones de ciclo y año de los cursos activos,
elimina duplicados de comisión y turno y conserva como opción la combinación
ya guardada al editar un producto. El valor persistido no cambia si luego se
modifica o desactiva un curso.

Se admiten estos casos:

1. Sin ciclo y sin curso: producto general.
2. Con ciclo y sin curso: producto destinado a todo el ciclo.
3. Con ciclo y curso: producto destinado a ese año dentro del ciclo.

Un curso sin ciclo es inválido. Al asignar una combinación por primera vez,
esta debe existir entre los cursos activos; no se consideran comisión ni
turno. Una combinación ya guardada puede conservarse aunque después todos los
cursos que la originaron queden inactivos.

## Imágenes

`ProductoServicio` incorporará una `foto` opcional. Es la imagen propia del
producto y se carga desde el admin técnico de Django. El MVP admite una sola
foto por producto; no incluye galerías.

`CategoriaProductoServicio` incorporará:

- `imagen_informativa`: imagen opcional compartida por los productos de la
  categoría;
- `titulo_imagen_informativa`: título público que explica el contenido de la
  imagen, por ejemplo `Tabla de talles` o `Cómo tomar las medidas`.

La imagen y su título se administran juntos. Una imagen informativa requiere
título y un título sin imagen es inválido. El concepto es deliberadamente
genérico: el modelo no supone que toda imagen compartida sea una tabla de
talles.

Las imágenes usan `ImageField` y siguen la política de medios ya documentada
por el proyecto. Ambos campos son opcionales y las pantallas no reservan
espacio cuando no hay imagen.

## Escenarios de precios

Se conservan `precio_asociados` y `precio_no_asociados`, pero ambos pasan a
admitir valores vacíos. No se agrega un campo de modalidad: el escenario se
deduce de la combinación de los dos importes y de `es_servicio`.

| Escenario | Precio asociados | Precio no asociados |
|---|---:|---:|
| Precio fijo diferenciado | informado | informado y diferente |
| Precio único | informado | informado e igual |
| Venta solo a asociados | informado | vacío |
| Servicio sin precio | vacío | vacío |

Las reglas son:

- los importes informados deben ser mayores que cero;
- informar solamente `precio_no_asociados` es inválido;
- un producto debe tener al menos `precio_asociados`;
- ambos importes vacíos solo son válidos cuando `es_servicio=True`;
- no se usa el valor cero para representar ausencia de precio.

El template presenta cada caso de forma explícita:

- el precio diferenciado conserva las columnas `Asociado` y `No asociado`;
- cuando ambos importes son iguales se muestra una sola columna `Precio`;
- cuando solo existe `precio_asociados`, se muestra `Precio asociado` junto a
  la etiqueta `Solo asociados`;
- un servicio sin precio no muestra `$0` ni celdas vacías: se identifica como
  `Sin precio` y su ficha prioriza descripción, condiciones y contacto.

## Ficha pública de categoría

La ficha conserva las dos columnas actuales. El panel derecho organiza los
productos activos en este orden:

1. productos generales;
2. Ciclo Básico;
3. Ciclo Superior;
4. dentro de cada ciclo, productos para todo el ciclo y luego grupos por año;
5. dentro de cada grupo, `orden` y luego `nombre`.

Cada fila puede mostrar una miniatura de la foto del producto. Cuando el
producto no tiene foto, no se muestra un espacio visual vacío. Toda la fila es
un único enlace accesible a la ficha individual; no abre un modal ni enlaza
directamente al archivo de imagen.

Una categoría puede mezclar escenarios de precios. Para conservar semántica
tabular, cada grupo contiguo de productos con el mismo escenario se renderiza
como una tabla propia con sus encabezados correspondientes. No se insertan
encabezados incompatibles ni celdas vacías dentro de una misma tabla.

Debajo de los grupos de precios se muestra la imagen informativa de la
categoría con su título. Luego se conserva el bloque de contacto de la
categoría. Si no hay destinatarios configurados, la ficha mantiene el aspecto
de tabla plana actual.

## Ficha pública individual

La ficha individual conserva breadcrumb, descripción y precios. Además:

- muestra la foto del producto en tamaño grande cuando existe;
- muestra el destinatario como ciclo o como ciclo y curso;
- muestra la imagen informativa y su título cuando la categoría los tiene.

Si el producto no tiene foto, se conserva la composición actual sin un
contenedor vacío. La navegación desde una fila llega a esta ficha y funciona
sin JavaScript.

## Separación de responsabilidades

- `models.py` define campos y validaciones estructurales.
- Un formulario de admin construye las opciones deduplicadas a partir de
  `Curso` y valida la combinación elegida.
- `selectors.py` consulta productos públicos y prepara la agrupación por ciclo
  y curso.
- `views.py` compone el contexto HTTP sin contener reglas de agrupación.
- Los templates renderizan los grupos ya preparados y aplican la mejora
  progresiva del enlace sobre la fila.

El admin y la auditoría incluirán los nuevos campos. La carga y edición seguirá
realizándose desde el admin técnico, de acuerdo con el alcance del MVP.

## Migración y compatibilidad

La migración agrega todos los campos como opcionales. Los productos y
categorías existentes quedan sin destinatario ni imágenes y conservan su
presentación y funcionamiento actuales.

No se transforma automáticamente ningún dato ni se crean relaciones con
`Curso`.

## Pruebas

Se cubrirán como mínimo:

- validación de producto general, producto para un ciclo y producto para un
  curso dentro de un ciclo;
- rechazo de curso sin ciclo y de combinaciones nuevas inexistentes;
- deduplicación de combinaciones de `Curso` sin considerar comisión ni turno;
- validación conjunta de imagen informativa y título;
- validación y clasificación de los cuatro escenarios de precios;
- orden y forma de los grupos preparados por el selector;
- exclusión de productos o categorías inactivos;
- fila enlazable y miniatura opcional en la ficha de categoría;
- foto grande, destinatario e imagen informativa en la ficha individual;
- ausencia de huecos o bloques vacíos cuando las imágenes no existen;
- conservación del comportamiento actual para datos previos a la migración.

## Especificación funcional a actualizar durante la implementación

- `especificacion/entidades/producto-servicio.md`;
- `especificacion/entidades/categoria-producto-servicio.md`;
- `especificacion/reglas/productos-servicios.md`;
- `especificacion/casos-de-uso/cu-listar-productos-servicios-publicos.md`;
- `especificacion/pantallas/sitio-publico.md`;
- `especificacion/arquitectura/media.md`, si las recomendaciones de tamaño o
  formato agregan una variante nueva.

## Fuera de alcance

- destinatarios por tipo de persona, como todos, asociados o adherentes;
- relación con una comisión o turno concreto;
- múltiples fotos por producto;
- tabla de talles estructurada como filas y columnas editables;
- modal de ampliación de la foto desde la categoría;
- precios desde, por unidad, escalonados, promocionales o por variante;
- pantalla propia de gestión fuera del admin técnico.
