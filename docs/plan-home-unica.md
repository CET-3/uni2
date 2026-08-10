# Plan: home única con hero por perfil

## Estado

Implementado sobre la rama `staging`.

Este documento conserva las decisiones que guiaron la implementación. La especificación OKF fue actualizada en el mismo trabajo y vuelve a ser la fuente de verdad del comportamiento vigente.

## Dependencias y orden

- Este es el plan base y no depende de los otros planes de navegación.
- Debe implementarse antes de `plan-navegacion-atencion-asociado.md`, porque define dónde vivirá el CTA administrativo y retira el dashboard de gestión.
- Debe implementarse antes de `plan-navegacion-publica-breadcrumbs.md`, porque convierte `/` en la home común para todos los perfiles y garantiza que las secciones públicas estén siempre disponibles.
- Los dos planes que dependen de este pueden implementarse en paralelo una vez terminada la home única.

## Objetivo

La raíz del sitio (`/`) debe renderizar siempre una única home. La sesión, los perfiles y los permisos del usuario solo modificarán el eyebrow, el título, el subtítulo y las acciones disponibles en el hero.

Debajo del hero se mostrarán siempre las secciones de la home pública actual:

- Servicios.
- Beneficios.
- Publicidades.
- Cómo asociarse.

El hero tendrá un máximo estricto de dos CTA. Si existen más acciones o perfiles disponibles, los accesos restantes aparecerán inmediatamente debajo del hero y antes de las secciones públicas.

## Variantes del hero

### Visitante sin sesión

Conservar exactamente el hero público actual:

- Eyebrow: `Mutual Escolar UNI2`.
- Título: `Tu mutual, más cerca que nunca`.
- Subtítulo actual.
- CTA `Sumate`.
- CTA `Iniciar sesión`.

### Asociado

Conservar los textos y acciones principales del dashboard actual de asociado:

- Eyebrow: `Mi panel`.
- Título: `Hola, {nombre del asociado}.`.
- Subtítulo actual del panel.
- CTA `Mi credencial`.
- CTA `Mis cuotas`.

### Comercio

Conservar los textos y la acción principal del dashboard actual de comercio:

- Eyebrow: `Mi comercio`.
- Título: nombre del comercio.
- Subtítulo actual del panel.
- CTA `Validar credencial`.

### Administración

Mostrar una variante orientada al trabajo interno:

- Eyebrow: `Administración interna`.
- Título: `Panel de gestión`.
- Subtítulo orientado a las tareas de la mutual.
- Hasta dos CTA correspondientes a acciones que el usuario tenga permiso para ejecutar.

La variante administrativa se detectará mediante permisos operativos y no por la pertenencia a un único grupo fijo. `Atención al asociado` tendrá prioridad como CTA cuando el usuario posea `gestion.consultar_asociados` y llevará a `gestion:asociados`.

La definición de acciones administrativas debe estar centralizada y ordenada. Esto permitirá que futuros permisos —por ejemplo, edición de publicidades— registren su etiqueta y destino sin llenar el hero de botones. Ningún CTA debe llevar a una pantalla que el usuario no tenga permiso para abrir.

### Usuario con más de un perfil

La home funcionará como selector de experiencia:

- Título: `Elegí cómo querés ingresar`.
- No mostrará el nombre del usuario ni un saludo con `Hola`.
- Mostrará hasta dos CTA de perfil.
- El orden de los perfiles será: asociado, comercio y administración.
- Si existe un tercer perfil, su acceso aparecerá inmediatamente debajo del hero.

Los CTA recargarán la misma home indicando la experiencia elegida:

- `/?perfil=asociado`
- `/?perfil=comercio`
- `/?perfil=gestion`

La home adoptará entonces el hero y las acciones de esa experiencia. El valor solicitado solo será aceptado si el perfil está disponible para el usuario autenticado. Un valor inválido o no autorizado volverá a mostrar el selector multiperfil.

La selección no se recordará en la sesión. Entrar nuevamente a `/` o tocar el logo volverá a mostrar el selector cuando haya más de un perfil.

## Acciones adicionales

Crear una sección compacta de accesos inmediatamente debajo del hero:

- Solo aparecerá cuando existan más de dos acciones o perfiles.
- No duplicará los CTA ya mostrados en el hero.
- Respetará los perfiles y permisos del usuario.
- Permitirá incorporar futuras funciones sin sobrecargar el hero.
- Después de esta sección comenzará el contenido público común.

## Cambios de navegación e implementación

- Sustituir el inicio inteligente y sus redirecciones por una única vista de home que cargue el contenido público y resuelva la variante del hero.
- Renderizar un único componente de hero alimentado por datos explícitos de contexto.
- Centralizar la detección de perfiles y el registro ordenado de acciones administrativas.
- Hacer que el login y el logo lleven siempre a `/`.
- Hacer que el logout vuelva a `/`, donde se mostrará la variante pública.
- Actualizar el menú multiperfil para utilizar `/?perfil=...`.
- Retirar el selector `/paneles/` y su template.
- Retirar los dashboards y rutas `/asociado/panel/`, `/comercio/panel/` y `/gestion/`.
- Conservar las pantallas operativas, como credencial, cuotas, validación de credenciales y listado de asociados.
- Retirar `/inicio/` como segunda home y eliminar el acceso `Sitio público`, dado que el contenido público estará siempre presente en `/`.
- Al implementar, actualizar las reglas de usuarios, navegación, sitio público y arquitectura dentro de la especificación OKF.

## Pruebas previstas

- Un visitante recibe `200` en `/` y ve el hero público actual.
- Asociado, comercio y administración reciben `200` en `/`, sin redirecciones a dashboards.
- Cada variante muestra el eyebrow, título, subtítulo y CTA correspondientes.
- La variante multiperfil muestra `Elegí cómo querés ingresar` y no incluye el nombre del usuario.
- Nunca aparecen más de dos CTA dentro del hero.
- Una tercera experiencia o acción aparece debajo del hero.
- `?perfil=` solo acepta perfiles disponibles para el usuario autenticado.
- Los accesos administrativos solo aparecen cuando el usuario posee el permiso correspondiente.
- Todas las variantes muestran las secciones públicas completas debajo de los accesos particulares.
- Login, logout, logo y menú respetan el nuevo flujo.
- Las antiguas rutas del selector y de los dashboards dejan de estar registradas.
