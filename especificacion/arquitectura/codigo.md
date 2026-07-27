---
type: "Arquitectura"
title: "Arquitectura actual del código"
description: "Organización por dominio y experiencia de usuario."
tags: [mvp, arquitectura]
timestamp: 2026-07-26T00:00:00-03:00
---

# Arquitectura actual del código

El código está organizado por dominio de negocio y por experiencia de usuario. La separación vigente busca que la app `usuarios` se ocupe de autenticación y roles, mientras que la app `gestion` concentra el backoffice usado por personal interno.

### Apps principales

- `usuarios`: login, logout, helpers de roles y navegación.
- `gestion`: dashboard simple de accesos, cobros, deudores, asociados y períodos de cuota.
- `asociados`: experiencia del asociado autenticado y su dominio.
- `comercios`: validación y panel del comercio adherido.
- `cuotas`: modelos y servicios de cuotas, deuda y pagos.
- `web`: home y páginas públicas del sitio.
- `contenidos`: productos, servicios y publicidades publicados por la web; en MVP se administran desde el admin técnico de Django.
- `especificacion`: visualizador interno de la especificación para desarrolladores staff. Ver [Visualizador de especificación](visualizador.md).

### Criterio de separación

- Las apps representan dominios de negocio o contextos técnicos bien delimitados.
- La carpeta `templates/gestion/` contiene pantallas de operación para usuarios con permisos de gestión.
- La carpeta `templates/asociados/` contiene el panel y vistas del asociado.
- La carpeta `templates/comercios/` contiene el flujo del comercio.
- La carpeta `templates/web/` agrupa el sitio público.
- El admin de Django queda como soporte técnico y no como navegación principal del backoffice.

### Archivos locales y datos operativos

El repositorio versiona el código, las migraciones, las pruebas, la especificación OKF y solamente datos de ejemplo sintéticos. Los padrones reales, las planillas de importación, los resultados de análisis, las bases de datos locales y los archivos media no se versionan. Deben guardarse en las rutas locales ignoradas por Git, como `data/`, `analisis_padron/` y `media/`.

Si una prueba necesita datos personales, debe usar información ficticia o anonimizada dentro de fixtures de prueba explícitas. Los prototipos temporales y la configuración personal de asistentes de desarrollo tampoco forman parte de la estructura del proyecto.

### Criterio de separación en la especificación

- `entidades/` describe estructura persistida: qué representa cada modelo, campos, estados, relaciones y restricciones de datos.
- `reglas/` es la fuente de verdad para comportamiento funcional reutilizable: cobros, mora, generación de cuotas, permisos, credenciales y validaciones.
- `casos-de-uso/` describe flujos operativos entre actor y sistema; debe enlazar reglas, no duplicarlas.
- `casos-borde/` documenta respuestas esperadas ante situaciones especiales.
- `pantallas/` describe qué se ve, desde dónde se opera y qué acciones ofrece cada experiencia.
- Las entidades pueden tener notas funcionales breves solo para orientar lectura, pero no deben repetir reglas de negocio completas.

### Inicio inteligente

La raíz (`/`) redirige según el perfil del usuario (ver [USUARIO-018](../reglas/usuarios.md#usuario-018--inicio-inteligente)). El logo de la aplicación sigue el mismo comportamiento. El menú de usuario incluye "Sitio público" para volver a la home pública desde cualquier experiencia.

El sistema no recuerda el último panel en el MVP. Cada visita a `/` o al logo vuelve a evaluar las experiencias disponibles.

### Dashboards y entradas

- Gestión: dashboard simple de `gestion` con accesos a las tareas permitidas para el usuario.
- El dashboard de gestión separa las tareas de operación diaria de las importaciones iniciales de puesta en marcha.
- Asociado autenticado: panel simple de `asociados` con accesos a credencial, cuotas, productos, servicios y comercios.
- Comercio autenticado: panel simple de `comercios` con acceso a validar credenciales.
- La navegación superior muestra el nombre del usuario autenticado como menú desplegable. El menú se organiza en secciones visuales: `Paneles`, `Herramientas` y `Cuenta`. Si tiene una sola experiencia, `Paneles` muestra el acceso directo a ese panel; si tiene más de una, lista los paneles disponibles. El acceso a gestión se muestra como `Panel de gestión`. `Herramientas` agrupa el admin técnico para usuarios `is_staff`, la especificación para usuarios con `gestion.ver_especificacion` y el design system para usuarios con `gestion.ver_design_system`. La sección `Cuenta` incluye "Sitio público" para todas las experiencias.

### Objetivo de la app gestión

- Evitar que tareas frecuentes dependan del admin genérico de Django.
- En el MVP, la gestión de productos, servicios, publicidades, comercios y actividades comerciales queda como excepción documentada y se resuelve desde el admin técnico de Django.
- Ofrecer pantallas operativas orientadas a flujo: buscar asociado, dar alta manual, ver detalle, editar datos, cobrar, ver deudores y administrar cuotas.
- No cargar el dashboard del MVP con métricas, rankings o reportes avanzados.
- Permitir una UX propia para escritorio y mobile sin contaminar la app de autenticación.
- Hacer más claro el mantenimiento: auth y roles en `usuarios`, backoffice en `gestion`.
- Registrar los permisos propios mediante un modelo técnico no gestionado por Django llamado `PermisoGestion`. Este modelo no representa una tabla de negocio: sirve para que las migraciones creen permisos personalizados de la app `gestion`.
- Controlar cada pantalla de gestión con permisos Django propios: ver dashboard de gestión, consultar asociados, editar asociados, importar asociados, exportar asociados, cobrar cuotas, ver deudores, administrar períodos de cuota e importar cuotas históricas.
- El comando `carga_inicial` crea datos de desarrollo con contenido de ejemplo del sitio público Vercel: 4 categorías de servicios (Fotocopias, Uniformes, Bicicleta solidaria, Cuadernillos y anillado) con productos asociados, 6 rubros de actividad comercial (Gastronomía, Actividad física, Belleza, Vestimenta, Educación, Tecnología y accesorios), 7 comercios adheridos con beneficios, 3 publicidades sin foto, grupos y permisos, cursos, un usuario admin, un usuario de atención de mutual vinculado también a un asociado de prueba, un usuario asociado vinculado a un asociado de prueba y un usuario comercio vinculado al comercio Librería Sur.
- Las fotos cargadas por admin técnico usan la configuración de archivos media documentada en [Archivos media](media.md).
- El límite técnico `DATA_UPLOAD_MAX_NUMBER_FIELDS` se eleva a `10000` para permitir acciones masivas razonables en el admin técnico luego de importaciones iniciales con muchas cuotas.
- En desarrollo local, `config.settings.local` acepta `localhost`, `127.0.0.1` y `192.168.18.138` como hosts permitidos. Esto permite levantar `runserver` en `0.0.0.0:8000` y probar la app desde un teléfono conectado a la misma red Wi-Fi.
- En producción sobre Vercel, las conexiones a Supabase no deben quedar persistentes entre requests y las migraciones no deben ejecutarse dentro del handler serverless. Las migraciones se corren como paso explícito de operación.
