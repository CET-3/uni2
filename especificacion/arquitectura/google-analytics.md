---
type: "Arquitectura"
title: "Medición de navegación con Google Analytics"
description: "Integración mínima de GA4 para medir visitas sin enviar identificadores ni URLs privadas."
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

## Identificación segura de las páginas

La etiqueta estándar no debe enviar automáticamente la ubicación real de la
página. Algunas rutas de Uni2 incluyen identificadores internos o tokens, por
ejemplo una credencial privada o el identificador de un asociado.

Cada vista de página se informa manualmente con el nombre estable que Django ya
asigna a la vista mediante `request.resolver_match.view_name`. Ejemplos:

| Página | Nombre informado |
| --- | --- |
| Inicio | `web:home` |
| Detalle de producto o servicio | `web:producto_servicio_detalle` |
| Resolución de una credencial | `usuarios:resolver_credencial` |
| Detalle de un asociado | `gestion:asociado_detalle` |
| Cuotas del asociado autenticado | `asociados:cuotas` |

El dato `page_location` usa una URL estadística construida con el origen
productivo y ese nombre de vista. No contiene parámetros de ruta, cadenas de
consulta ni fragmentos. El `page_title` también usa un nombre estable y no el
título visible, porque algunas pantallas muestran nombres de comercios,
productos u otras entidades.

El referente enviado a Google no conserva rutas, parámetros ni fragmentos. Se
limita al origen del referente para evitar que una navegación anterior filtre
un token o identificador. La secuencia de eventos `page_view` sigue permitiendo
analizar el recorrido general entre tipos de pantalla.

La URL visible, los títulos mostrados en el navegador y la navegación de la
aplicación no cambian. La normalización afecta solamente los datos enviados a
Analytics.

## Integración en Django

La responsabilidad se divide de forma explícita:

- la configuración decide si Analytics está habilitado;
- un procesador de contexto expone únicamente el identificador de medición y
  el nombre seguro de la vista;
- un componente de template carga `gtag.js` y envía un único `page_view`;
- `templates/base.html` incluye ese componente para cubrir las páginas que
  comparten el layout principal.

No se incorpora Google Tag Manager ni una dependencia externa de Django. Para
este alcance, la etiqueta directa es más pequeña y deja toda la configuración
relevante versionada en el proyecto.

## Configuración de GA4

La medición automática de vistas de página debe estar desactivada para evitar
que Google reciba la URL real o duplique eventos. También deben quedar
desactivados los eventos adicionales de medición mejorada que no forman parte
del alcance acordado.

No se configura `user_id`, dimensiones personalizadas con datos de personas ni
datos obtenidos de los modelos de Uni2.

## Verificación

Las pruebas automatizadas deben comprobar que:

- Producción carga la etiqueta cuando el identificador es válido;
- local y staging no cargan la etiqueta;
- la página vista usa el nombre de la vista y no incluye parámetros reales;
- una ruta privada de credencial no expone su UUID en el HTML de Analytics;
- una ruta de gestión no expone el identificador del asociado;
- si la variable no está definida, el sitio funciona sin realizar medición.

Después del despliegue se verifica una navegación controlada con Tag Assistant
y el informe en tiempo real de GA4. No deben aparecer UUID, identificadores de
asociados ni cadenas de consulta.

