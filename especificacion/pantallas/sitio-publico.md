---
type: "Pantalla"
title: "Sitio público"
description: "Sitio público"
tags: [mvp, pantalla]
timestamp: 2026-06-24T00:00:00-03:00
---

# Sitio público

- Inicio.
  - Hero: presentación de la mutual con título, descripción y botones de acción ("Asociate", "Iniciar sesión").
  - Servicios: grilla de `CategoriaProductoServicio` activas. Cada card muestra nombre, descripción y enlace al listado completo.
  - Beneficios: grilla de rubros (`ActividadComercial`) que tienen al menos un comercio con estado `Firmado`. Cada card muestra hasta 3 fotos de comercios del rubro en un diseño de "nube de logos" (izquierda, centro, derecha) con el nombre del rubro como etiqueta inferior. Las fotos se toman del campo `foto` de cada `Comercio`. Si un rubro tiene menos de 3 comercios con foto, se centran los disponibles. Cada card enlaza al detalle de la actividad comercial.
  - Nuestros favoritos: publicidades activas en cards. Cada card muestra foto, etiqueta principal, título, etiqueta secundaria (descuento), descripción y enlace al detalle vinculado (producto/servicio o comercio).
  - Cómo asociarse: cuatro pasos numerados con indicaciones e información de cuota social y horarios de atención en tabla.
- Productos y servicios.
  - Categoría detalle (`/servicios/<pk>/`): muestra nombre, ícono y descripción de la categoría, grilla de productos/servicios activos con precios diferenciados para asociados y no asociados, y texto CTA configurable. Incluye breadcrumb (Inicio > Productos y servicios > {categoría}).
  - Actividad comercial detalle (`/actividades-comerciales/<pk>/`): breadcrumb Inicio > Comercios > {actividad comercial}, nombre de la actividad, listado de comercios firmados con dirección, beneficio, teléfono y presencia web. Botón "← Todos los comercios".
- Comercios: listado público vertical de comercios con estado `Firmado`, ordenado por `orden`.
  - Comercio detalle (`/comercios/<pk>/`): muestra nombre, actividad comercial, dirección, beneficio, teléfono, email y presencia web si el comercio está `Firmado`. Si el comercio no está firmado, muestra mensaje "Este comercio estará disponible próximamente" con enlace "Ver comercios adheridos".
- Login.
