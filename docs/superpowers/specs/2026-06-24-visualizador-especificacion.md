# Visualizador de especificación para staff

## Problema

Los alumnos que trabajan en la app necesitan poder leer la especificación (archivos Markdown en `especificacion/`) desde el navegador, sin tener que abrir los archivos en el editor.

## Solución

Crear una app `especificacion` que lee los archivos `.md` del bundle OKF y los muestra como texto plano monospace, accesible solo para usuarios staff.

## Cambios

### especificacion/ (nueva app)

```
especificacion/
├── __init__.py
├── apps.py
├── urls.py
├── views.py
└── templates/
    └── especificacion/
        └── archivo.html
```

### especificacion/views.py

- `IndiceView` (TemplateView): lee `especificacion/index.md`, lo pasa como contexto `contenido_md`
- `ArchivoView` (TemplateView): recibe `ruta` por URL, construye la ruta absoluta dentro de `especificacion/`, lee el archivo, lo pasa como `contenido_md`. Validación de seguridad: rechazar si la ruta intenta salir de `especificacion/`.
- Ambos usan `StaffMemberRequiredMixin` para restringir acceso solo a `is_staff=True`.

### especificacion/urls.py

```
especificacion/
├── ''              → IndiceView        (name: indice)
├── <path:ruta>/    → ArchivoView       (name: archivo)
```

### especificacion/templates/especificacion/archivo.html

- Extiende `base.html`
- Muestra el contenido Markdown en un `<pre>` con clase `font-monospace`
- Estilo limpio, fondo claro, scroll horizontal para líneas largas
- Breadcrumb indicando la ruta del archivo

### config/urls.py

- Agregar `path("especificacion/", include("especificacion.urls"))`

### templates/includes/navbar.html

- Agregar link "Especificación" a `especificacion:indice` dentro de un `{% if user.is_staff %}` visible solo para staff

## Lo que no cambia

- Archivos de especificación existentes (`especificacion/**/*.md`) — sin modificaciones
- Modelos, selectors, services, admin — sin cambios
- Otras apps (`web`, `gestion`, `asociados`, etc.) — sin cambios
- No se instalan librerías nuevas

## Seguridad

- Todos los views chequean `is_staff` antes de mostrar contenido
- `ArchivoView` computa `os.path.realpath()` y verifica que el resultado comience con `BASE_DIR / "especificacion"` (protección contra path traversal)

## Tests

- `test_indice_staff_access`: staff ve 200, anónimo ve 302/403
- `test_indice_contenido`: el índice contiene la especificación
- `test_archivo_valido`: un archivo conocido responde 200
- `test_archivo_inexistente`: un archivo que no existe responde 404
- `test_archivo_path_traversal`: rutas con `../` son rechazadas
