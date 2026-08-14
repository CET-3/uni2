# Diseño: layout vertical de la categoría de productos y servicios

## Objetivo

Alinear la ficha pública de una categoría con la jerarquía visual del diseño
original: primero se presenta el título grande y su descripción; debajo aparece
el listado completo de productos o servicios.

El cambio afecta únicamente a `/servicios/<pk>/`. La ficha individual de un
producto o servicio conserva su composición en dos columnas.

## Decisión de diseño

La ficha de categoría deja de usar `uni2-detail-layout`, porque ese componente
distribuye la introducción y el panel en dos columnas en desktop. En su lugar
usa una variante propia con flujo vertical:

1. breadcrumb;
2. encabezado con nombre y descripción de la categoría;
3. panel de contenido a todo el ancho;
4. productos generales, cuando existen;
5. secciones de Ciclo Básico y Ciclo Superior;
6. dentro de cada ciclo, productos para todo el ciclo y luego cursos;
7. tablas agrupadas de productos o servicios;
8. imagen informativa compartida, cuando existe;
9. bloque de contacto, cuando existe.

El encabezado y el panel comparten el mismo contenedor. El espacio entre ambos
debe conservar una lectura clara sin introducir una card adicional alrededor
del título.

## Jerarquía de ciclos y cursos

El selector deja de entregar una lista plana con títulos combinados como
`Ciclo Básico · 1ro`. Preparará una estructura explícita con:

- un bloque opcional de productos generales;
- una colección ordenada de ciclos;
- dentro de cada ciclo, un bloque opcional `Para todo el ciclo` y los cursos
  ordenados;
- dentro de cada curso, los grupos contiguos por escenario de precio.

Los títulos públicos de curso usan la forma `1.º C.B.`, `2.º C.B.`, `1.º C.S.`
y equivalentes, sin distinguir comisión ni turno.

## Comportamiento responsive

En desktop ancho se muestran Ciclo Básico y Ciclo Superior lado a lado. En
mobile, cuando existen ambos ciclos, aparecen dos botones para alternar cuál se
muestra. Ciclo Básico queda seleccionado inicialmente. Si solo existe un ciclo,
el selector no se muestra. Los productos generales permanecen visibles y fuera
del selector.

Los botones exponen su relación con cada panel mediante `aria-controls` y su
estado mediante `aria-selected`. El contenido se renderiza completo desde
Django: sin JavaScript se muestran ambos ciclos. Un script específico activa
la alternancia solamente en el breakpoint mobile y vuelve a mostrar ambos
paneles al pasar a desktop.

Cada ciclo se presenta como una card independiente. En desktop ancho se ubican
lado a lado; en anchos intermedios se apilan y en mobile queda visible solamente
la card elegida. Ciclo Básico usa el azul de marca como acento superior y en su
identificador; Ciclo Superior usa el verde de marca. Los productos generales,
cuando existen, se muestran antes en una card neutral de ancho completo.

Las tablas conservan su comportamiento responsive actual. El bloque de contacto
mantiene ícono y texto en una misma fila; el texto puede envolver dentro de su
columna sin desplazar el ícono a una fila independiente.

## Alcance conservado

Este cambio no modifica modelos ni reglas de precio. Se mantienen:

- agrupación por ciclo y curso;
- encabezado `Producto`, `Servicio` o `Producto o servicio` según los ítems;
- importes alineados a la derecha;
- omisión de la columna de precio para grupos sin precio;
- miniatura y enlace único por fila;
- imagen informativa y contacto opcionales.

La ficha individual continúa usando `uni2-detail-layout`: información y foto a
la izquierda, precios o condiciones a la derecha.

## Implementación

La plantilla de categoría incorporará una clase explícita para su flujo
vertical. El CSS limitará los nuevos estilos a esa clase para no cambiar las
fichas individuales ni las páginas de comercios.

`contenidos/selectors.py` preparará la jerarquía general/ciclo/curso. La vista
solo pasará esa estructura al template. Un archivo JavaScript pequeño y
específico controlará el selector mobile; no contendrá decisiones de negocio.

La especificación funcional de la pantalla se actualizará en
`especificacion/pantallas/sitio-publico.md` para reemplazar la descripción de
dos columnas por la nueva jerarquía vertical.

## Pruebas

Se verificará que:

- la categoría use el contenedor vertical y no `uni2-detail-layout`;
- el encabezado aparezca antes del panel de productos;
- la estructura agrupe primero por ciclo y luego por curso;
- los productos generales queden fuera de los paneles de ciclo;
- el selector mobile solo aparezca cuando existan ambos ciclos;
- los botones actualicen `aria-selected` y la visibilidad del panel asociado;
- sin JavaScript permanezcan visibles todos los ciclos;
- las tablas y bloques opcionales continúen renderizándose;
- la ficha individual mantenga `uni2-detail-layout`;
- la suite completa no presente regresiones;
- una revisión visual en desktop y mobile confirme el orden y ancho esperados.

## Fuera de alcance

- cambiar el layout de la ficha individual;
- rediseñar las tablas o la agrupación contigua por escenario de precio;
- modificar datos o migraciones;
- cambiar la navegación o los breadcrumbs.
