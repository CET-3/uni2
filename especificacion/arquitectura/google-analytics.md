---
type: "Arquitectura"
title: "Medición de navegación con Google Analytics"
description: "Integración estándar de GA4 para medir visitas con las URLs originales del navegador."
tags: [mvp, arquitectura, analytics, privacidad, produccion]
timestamp: 2026-08-17T00:00:00-03:00
---

# Medición de navegación con Google Analytics

Uni2 usa Google Analytics 4 únicamente para conocer visitas y navegación entre
pantallas. La integración alcanza al sitio público y a las experiencias
autenticadas de asociados, comercios y gestión.

No se registran eventos funcionales personalizados. En particular, no se
informa a Analytics cuándo una persona inicia sesión, consulta cuotas, valida
una credencial o registra un pago.

## Ambientes

La etiqueta de Google se carga solamente en Producción y únicamente cuando
existe un identificador de medición configurado. Desarrollo local y staging no
envían información a la propiedad productiva, aunque reciban por error una
variable con el mismo nombre.

La configuración usa `GOOGLE_ANALYTICS_MEASUREMENT_ID`. El identificador
empieza con `G-`, no es una credencial secreta y se administra como variable de
entorno para poder activar o desactivar la medición sin modificar plantillas.

## Identificación original de las páginas

Uni2 usa el comportamiento estándar de GA4. Cada vista de página informa la
URL completa, el referente y el título que conoce el navegador. No se construye
una ruta estadística alternativa ni se reemplazan esos valores por el nombre
interno de la vista Django.

Esta decisión permite analizar las páginas y parámetros tal como se navegan,
pero implica que Google Analytics puede recibir parámetros de ruta, cadenas de
consulta, fragmentos, IDs internos y tokens incluidos en la URL. Por ejemplo,
una visita a una credencial puede incluir su UUID y una visita al detalle de un
asociado puede incluir su ID. La propiedad de Analytics y sus accesos deben
administrarse considerando esa exposición.

## Integración en Django

La responsabilidad se divide de forma explícita:

- la configuración decide si Analytics está habilitado;
- un procesador de contexto expone únicamente el identificador de medición;
- un componente de template carga `gtag.js` y ejecuta su configuración estándar;
- `templates/base.html` incluye ese componente para cubrir las páginas que
  comparten el layout principal.

No se incorpora Google Tag Manager ni una dependencia externa de Django. Para
este alcance, la etiqueta directa es más pequeña y deja toda la configuración
relevante versionada en el proyecto.

## Configuración de GA4

La medición automática de vistas de página queda activa. El llamado estándar
`gtag("config", measurement_id)` genera el `page_view`; Uni2 no envía otro evento
manual ni define `page_location`, `page_referrer` o `page_title`.

Los eventos adicionales de medición mejorada que no forman parte del alcance
acordado deben permanecer desactivados.

No se configura `user_id`, dimensiones personalizadas con datos de personas ni
datos obtenidos de los modelos de Uni2.

## Verificación

Las pruebas automatizadas deben comprobar que:

- Producción carga la etiqueta cuando el identificador es válido;
- local y staging no cargan la etiqueta;
- el componente usa la configuración estándar y no construye rutas
  `/__analytics__/`;
- no se envían manualmente `page_location`, `page_referrer`, `page_title` ni un
  segundo evento `page_view`;
- si la variable no está definida, el sitio funciona sin realizar medición.

Después del despliegue se verifica una navegación controlada con Tag Assistant
y el informe en tiempo real de GA4. Las ubicaciones deben coincidir con las URLs
originales navegadas, incluidos sus parámetros cuando existan.
