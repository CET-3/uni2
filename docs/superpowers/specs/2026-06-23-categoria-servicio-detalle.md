# Vista de detalle por categoría de servicio

## Problema
La home enlaza cada card de servicio a `productos_servicios.html#{{ categoria.nombre|slugify }}` pero la página destino no tiene `id` en las secciones, por lo que el anchor no funciona. No existe una vista dedicada que muestre los productos de una sola categoría.

## Solución
Agregar una vista `CategoriaProductoServicioDetalleView` en la app `web` que recibe un pk de categoría y muestra sus productos/servicios activos.

## Cambios

### web/views.py
- Nueva `CategoriaProductoServicioDetalleView` (DetailView de `CategoriaProductoServicio`)
- Template: `web/categoria_detalle.html`

### web/urls.py
- `servicios/<int:pk>/` → `web:categoria_detalle`

### templates/web/categoria_detalle.html
- Encabezado: nombre, ícono, descripción
- Grilla de productos con nombre, tipo, descripción, precios
- CTA de la categoría al pie
- Botón "Volver" al listado general `/productos-servicios/`

### templates/web/home.html
- Cada "Ver más" linkea a `web:categoria_detalle pk=categoria.pk`

### templates/web/productos_servicios.html
- Cada `<section>` recibe `id="{{ categoria.nombre|slugify }}"` para que los anchors funcionen

## Lo que no cambia
- `productos_servicios.html` (listado general) sigue igual
- `producto_servicio_detalle.html` (detalle individual) sigue igual
- Modelos, selectors, servicios — sin cambios

## Tests
- test_categoria_detalle: status 200, template correcto, productos visibles
- test_categoria_detalle_404: pk inexistente
