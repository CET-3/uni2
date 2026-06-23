# Vista de detalle por actividad comercial

## Problema
La home enlaza cada card de beneficio (rubro) a la lista general de comercios. No existe una vista dedicada que muestre solo los comercios de una actividad comercial específica.

## Solución
Agregar una vista `ActividadComercialDetalleView` en la app `web` que recibe un pk de actividad comercial y muestra sus comercios firmados activos.

## Cambios

### web/views.py
- Nueva `ActividadComercialDetalleView` (DetailView de `ActividadComercial`)
- Template: `web/actividadcomercial_detalle.html`

### web/urls.py
- `actividades-comerciales/<int:pk>/` → `web:actividad_comercial_detalle`

### templates/web/actividadcomercial_detalle.html
- Breadcrumb: Inicio > Comercios > {actividad comercial}
- Encabezado: nombre de la actividad comercial
- Grilla de comercios con nombre, dirección, beneficio, teléfono, presencia web
- Botón "Volver" al listado general `/comercios/`

### templates/web/home.html
- Cada rubro en Beneficios linkea a `actividad_comercial_detalle pk=rubro.pk`

## Lo que no cambia
- `comercios.html` (listado general) sigue igual
- `comercio_detalle.html` (detalle individual) sigue igual
- Modelos, selectors, servicios — sin cambios

## Tests
- test_actividad_comercial_detalle: status 200, template correcto, comercios visibles
- test_actividad_comercial_detalle_404: pk inexistente o actividad sin comercios firmados
