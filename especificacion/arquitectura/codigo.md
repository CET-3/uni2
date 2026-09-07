---
type: "Arquitectura"
title: "Arquitectura actual del código"
description: "Organización por dominio y experiencia de usuario."
tags: [mvp, arquitectura]
timestamp: 2026-07-29T00:00:00-03:00
---

# Arquitectura actual del código

El código está organizado por dominio de negocio y por experiencia de usuario. La separación vigente busca que la app `usuarios` se ocupe de autenticación y roles, mientras que la app `gestion` concentra el backoffice usado por personal interno.

### Apps principales

- `usuarios`: login, logout, helpers de roles y navegación.
- `gestion`: cobros, deudores, asociados, auditoría y períodos de cuota; sus accesos se presentan desde la home común.
- `auditoria`: historial inmutable, serialización segura y soporte común para services y admin.
- `asociados`: experiencia del asociado autenticado y su dominio.
- `comercios`: validación y panel del comercio adherido.
- `cuotas`: modelos y servicios de cuotas, deuda y pagos.
- `web`: home y páginas públicas del sitio.
- `contenidos`: productos, servicios y publicidades publicados por la web; en MVP se administran desde el admin técnico de Django.
- `comunicaciones`: registro y entrega de mensajes por correo; prepara una
  frontera común para lotes y push futuros sin trasladar reglas desde los
  dominios que originan cada aviso.
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

### Home única

La raíz (`/`) siempre renderiza `web/home.html` (ver [USUARIO-018](../reglas/usuarios.md#usuario-018--home-única-por-experiencia)). `usuarios/home_navigation.py` compone la presentación y las acciones autorizadas sin colocar esa decisión en el template. La vista `web` agrega los contenidos públicos y coordina ambas partes.

El logo y el login vuelven a `/`. Un usuario multiperfil puede elegir una experiencia mediante `?perfil=`, pero el sistema no la guarda en sesión. No existen una home pública paralela, un selector separado ni dashboards por dominio.

### Experiencias y entradas

- La variante de asociado enlaza directamente a credencial y cuotas.
- La variante de comercio enlaza directamente a validación de credenciales.
- La variante administrativa construye una lista ordenada de acciones según permisos. El hero toma las primeras dos y `Más accesos` muestra el resto.
- La navegación superior muestra el nombre del usuario autenticado como menú desplegable. El menú se organiza en `Experiencias`, `Herramientas` y `Cuenta`. `Experiencias` enlaza a las variantes de la home; `Herramientas` conserva admin técnico, especificación y design system según permisos; `Cuenta` contiene instalación PWA y cierre de sesión.

### Objetivo de la app gestión

- Evitar que tareas frecuentes dependan del admin genérico de Django.
- En el MVP, la gestión de productos, servicios, publicidades, comercios y actividades comerciales queda como excepción documentada y se resuelve desde el admin técnico de Django.
- Ofrecer pantallas operativas orientadas a flujo: buscar asociado, dar alta manual, ver detalle, editar datos, cobrar, ver deudores y administrar cuotas.
- No cargar la home administrativa con métricas, rankings o reportes avanzados.
- Permitir una UX propia para escritorio y mobile sin contaminar la app de autenticación.
- Hacer más claro el mantenimiento: auth y roles en `usuarios`, backoffice en `gestion`.
- Registrar los permisos propios mediante un modelo técnico no gestionado por Django llamado `PermisoGestion`. Este modelo no representa una tabla de negocio: sirve para que las migraciones creen permisos personalizados de la app `gestion`.
- Controlar cada pantalla de gestión con permisos Django propios. La experiencia administrativa se deduce de los permisos operativos reales o de la capacidad de acceder al admin técnico; no usa un permiso separado de dashboard. Las capacidades concretas controlan consulta y edición de asociados, importaciones, exportación, cobros, deudores, períodos, documentación y auditoría.
- El comando `carga_inicial` crea datos ficticios para desarrollo local: 4 categorías de servicios (Fotocopias, Uniformes, Bicicleta solidaria, Cuadernillos y anillado) con productos asociados, 6 rubros de actividad comercial (Gastronomía, Actividad física, Belleza, Vestimenta, Educación, Tecnología y accesorios), 7 comercios adheridos con beneficios, 3 publicidades sin foto, cursos, un superusuario en `Administrador de la app`, un usuario de Atención al asociado vinculado también a un asociado de prueba, un usuario asociado y un usuario comercio vinculado al comercio Librería Sur. Reutiliza el servicio de [configuración de grupos](configuracion-grupos.md), sin duplicar la matriz. El setting explícito `ALLOW_DEMO_DATA` lo habilita solamente en desarrollo local y tests; producción lo rechaza.
- El comando `importar_comercios_xlsx` realiza la carga inicial real de comercios desde una planilla local. Sin `--confirmar` solo analiza y valida; con `--confirmar` crea o actualiza comercios y actividades, y guarda las imágenes embebidas mediante el storage configurado. La lectura y las reglas de importación viven en `comercios/importers.py`, mientras que el comando se limita a coordinar la entrada y mostrar el resultado.
- El formato monetario visible se centraliza en `config/formatting.py`. Los templates usan el filtro `moneda` de `web/templatetags/formatos.py`; los valores técnicos de inputs, JavaScript e importadores no se localizan.
- El admin técnico autoriza cuentas activas con algún permiso efectivo sobre un modelo registrado. La comprobación vive en `usuarios.admin_access` y reutiliza los permisos de cada `ModelAdmin`; no depende de nombres de grupos ni recalcula `is_staff`.
- Las fotos cargadas por admin técnico usan la configuración de archivos media documentada en [Archivos media](media.md).
- El límite técnico `DATA_UPLOAD_MAX_NUMBER_FIELDS` se eleva a `10000` para permitir acciones masivas razonables en el admin técnico luego de importaciones iniciales con muchas cuotas.
- En desarrollo local, `config.settings.local` acepta `localhost`, `127.0.0.1` y `192.168.18.138` como hosts permitidos. Esto permite levantar `runserver` en `0.0.0.0:8000` y probar la app desde un teléfono conectado a la misma red Wi-Fi.
- En producción sobre Vercel, las conexiones a Supabase no deben quedar persistentes entre requests. El arranque de la aplicación se limita a exponer la aplicación HTTP: no consulta el esquema, no ejecuta migraciones y no carga datos. La detección y el empaquetado de Django quedan a cargo del soporte nativo de Vercel. Ver [Despliegue en Vercel](despliegue.md).
