---
type: "Pantalla"
title: "Sitio público"
description: "Sitio público"
tags: [mvp, pantalla]
timestamp: 2026-06-24T00:00:00-03:00
---

# Sitio público

- Inicio.
  - Hero: presentación de la mutual con título, descripción y botones de acción ("Asociate", "Iniciar sesión"). Usa componentes productivos `uni2-hero`, `uni2-section-inner`, `uni2-eyebrow`, `uni2-hero-actions` y `uni2-cta`. El fondo usa diagonales con los colores de marca y mantiene esa dirección también en mobile para que la composición no se corte debajo del contenido.
  - Servicios: grilla visual con `uni2-service-grid` y `uni2-service-card` para los servicios principales de la mutual. Cada card muestra ícono, nombre, descripción y enlace cuando corresponda. La home productiva usa el mismo patrón visual que el bloque `Servicios` del design system interno, sin depender de `ds-page`.
  - Beneficios: grilla de rubros (`ActividadComercial`) que tienen al menos un comercio con estado `Firmado`. La home usa la misma estructura visual del bloque `Club de Beneficios` del design system (`uni2-benefit-band`, `uni2-benefit-links`, `uni2-benefit-mix-card` y `uni2-benefit-rubric`). La nube de logos reales se arma con `uni2-benefit-logo-cloud` y `uni2-benefit-logo-dot`. Cada card muestra hasta 3 fotos de comercios del rubro en un diseño de "nube de logos" (izquierda, centro, derecha) con el nombre del rubro como etiqueta inferior. Las fotos se toman del campo `foto` de cada `Comercio`. Si un rubro tiene menos de 3 comercios con foto, se centran los disponibles. El bloque se muestra como grilla de cards visibles en pantalla: tres cards por fila desde el ancho de tablet y dos cards por fila en mobile. Cada card enlaza al detalle de la actividad comercial.
  - Nuestros favoritos: publicidades activas en cards productivas `uni2-ad-card`, con `uni2-badge` para etiqueta principal y `uni2-discount` para etiqueta secundaria. Cada card muestra etiqueta principal, título, etiqueta secundaria (descuento), descripción y enlace al detalle vinculado (producto/servicio o comercio). Si la publicidad tiene foto, la muestra como imagen de fondo; si no tiene foto, se muestra con una presentación simple sin imagen.
  - Cómo asociarse: cuatro pasos numerados con `uni2-steps`, `uni2-step-card` y `uni2-step-number`, más información de cuota social y horarios de atención en `uni2-info-box` y `uni2-hours-table`. En mobile, los horarios cambian a tarjetas compactas con chips de horario para que no se desborde la tabla.
  - Footer: enlaces de contacto, ubicación y texto institucional. En mobile se apila en una columna compacta, sin reservar espacio para barras flotantes que no existen en la implementación Django.
- Productos y servicios.
  - Categoría detalle (`/servicios/<pk>/`): muestra nombre, ícono y descripción de la categoría, grilla de productos/servicios activos con precios diferenciados para asociados y no asociados, y texto CTA configurable. Incluye breadcrumb (Inicio > Productos y servicios > {categoría}).
  - Actividad comercial detalle (`/actividades-comerciales/<pk>/`): nombre de la actividad y listado de comercios firmados en formato de lista de beneficios compartida con el design system. Cada card muestra logo o foto circular, nombre, beneficio en un badge único, dirección, teléfono y presencia web cuando existen. No muestra breadcrumb, botón de retorno ni rótulo intermedio en el encabezado.
- Comercios: listado público vertical de comercios con estado `Firmado`, ordenado por `orden`.
  - Comercio detalle (`/comercios/<pk>/`): muestra logo o iniciales, nombre, actividad comercial, beneficio, dirección, teléfono, email y, cuando existe, un CTA único "Visitar online" hacia la presencia web del comercio. La dirección se muestra inmediatamente después del beneficio, en un bloque propio igual al teléfono. El listado de comercios usa el mismo texto "Visitar online" para la presencia web. Si el comercio no está firmado, muestra mensaje "Este comercio estará disponible próximamente" con enlace "Ver comercios adheridos".
- Login.
