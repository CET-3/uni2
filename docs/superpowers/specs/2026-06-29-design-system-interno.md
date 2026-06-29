# Design system interno para Uni2

## Contexto

El proyecto ya tiene una base visual tomada de `PAGINA-WEB` y un showcase parcial en `templates/web/design-system.html`. La referencia visual completa existe fuera del repo en `/home/milena/CET3/PAGINA-WEB/design-system.html`.

La especificación funcional ya se puede consultar desde el navegador en `/especificacion/` con permiso de gestión. El design system debe quedar expuesto de forma parecida: accesible para quienes desarrollan o mantienen pantallas, pero no como página pública del sitio.

## Alcance de esta etapa

Esta etapa porta y publica el design system como documentación visual interna.

Incluye:

- Portar el contenido completo del HTML externo al proyecto Django.
- Adaptar rutas de CSS, imágenes, enlaces y scripts para que funcionen dentro del repo.
- Proteger `/design-system/` con un permiso Django propio.
- Agregar la entrada "Design system" al menú del usuario solo cuando tenga ese permiso.
- Documentar en la especificación OKF cómo se usa el design system como referencia obligatoria para pantallas nuevas o rediseños.

No incluye:

- Rediseñar pantallas existentes.
- Migrar todos los templates actuales al nuevo sistema visual.
- Crear una app frontend nueva.
- Reemplazar Django Templates o Bootstrap.

La migración visual de pantallas existentes queda para una segunda etapa, pantalla por pantalla.

## Decisión de arquitectura

La URL pública sigue siendo `/design-system/`, pero deja de ser una página abierta. La vista se mantiene simple y renderiza un template Django con el showcase visual.

Se agrega un permiso separado:

```python
GESTION_VER_DESIGN_SYSTEM = "gestion.ver_design_system"
```

La separación evita mezclar dos responsabilidades:

- `gestion.ver_especificacion`: leer la especificación funcional.
- `gestion.ver_design_system`: leer la referencia visual y criterios de UI.

Ambos permisos pueden asignarse a los mismos grupos, pero el código y la documentación mantienen el propósito explícito de cada uno.

## Navegación

El dropdown del usuario autenticado agrega una opción "Design system" cuando `perms.gestion.ver_design_system` sea verdadero.

La opción se ubica junto a "Especificación" porque ambas son herramientas internas de consulta para desarrollo, operación y mantenimiento. No aparece en la navegación pública principal.

## Port del HTML externo

El archivo de origen es:

```text
/home/milena/CET3/PAGINA-WEB/design-system.html
```

El template destino conserva el contenido visual completo, pero adapta lo necesario para Django:

- Reemplaza `style2.css` por CSS versionado dentro de `static/css/`.
- Reemplaza `LOJO_UNI2.png` por una imagen disponible en `static/img/`.
- Cambia enlaces a páginas estáticas `.html` por URLs Django existentes o por anclas internas cuando sean solo referencia.
- Evita que imágenes inexistentes de `assets/logos/...` rompan la experiencia; si no existen en este repo, se reemplazan por placeholders visuales o se documenta que son ejemplos.
- Mantiene Bootstrap 5 como base.

## Permisos y grupos iniciales

El nuevo permiso se agrega a la lista de permisos propios de `gestion` y a la migración correspondiente.

El comando de carga inicial asigna el permiso a los perfiles que necesitan consultar material interno de trabajo:

- `Atención de mutual`.
- `Administradores` o grupo equivalente que recibe todos los permisos de gestión.

## Regla de trabajo para estudiantes

A partir de esta etapa, toda pantalla nueva y todo rediseño de pantalla existente debe partir del design system.

La regla práctica es:

1. Buscar primero si el patrón visual ya existe en `/design-system/`.
2. Si existe, usar ese patrón con Django Templates y Bootstrap.
3. Si no existe, definir el patrón en el design system o documentar la decisión en la especificación antes de aplicarlo en una pantalla.
4. Evitar estilos sueltos en templates salvo ajustes mínimos y justificados.

Esto mantiene el proyecto enseñable: las decisiones visuales viven en una referencia compartida y no quedan escondidas en cada template.

## Testing

Tests esperados para esta etapa:

- Usuario anónimo no puede acceder a `/design-system/`.
- Usuario autenticado sin `gestion.ver_design_system` recibe 403.
- Usuario con `gestion.ver_design_system` puede ver la página.
- El menú muestra "Design system" solo cuando el usuario tiene el permiso.

También se revisa que el template renderice sin errores.

## Riesgos

El HTML externo incluye dependencias y rutas que no pertenecen al repo Django. El port debe corregirlas de forma explícita para no dejar referencias rotas.

La página puede quedar visualmente extensa. Eso es aceptable porque funciona como showcase interno, no como pantalla operativa frecuente.
