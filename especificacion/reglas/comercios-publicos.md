---
type: "Regla de negocio"
title: "Comercios públicos"
description: "Reglas de negocio sobre publicación y visualización de comercios."
tags: [mvp, reglas]
timestamp: 2026-07-29T00:00:00-03:00
---

# Comercios públicos

Estas reglas describen cómo se cargan, mantienen y muestran los comercios adheridos
en el sitio público.

1. En el sitio público se muestran los comercios con estado `Firmado`.
2. El estado del comercio se selecciona desde una lista fija definida en el sistema. No se administra como entidad independiente.
3. Los comercios publicados se listan de acuerdo al atributo `orden`.
4. El detalle público de un comercio (`/comercios/<pk>/`) está disponible para cualquier comercio existente, independientemente de su estado. Si el comercio tiene estado `Firmado`, se muestran sus datos completos. Si tiene otro estado (`Pendiente`, `Vencido` o `Baja`), se muestra una pantalla informativa con el mensaje "Este comercio estará disponible próximamente" y un enlace para volver al listado de comercios.
5. En la sección Beneficios de la home se muestran hasta 3 comercios con foto por cada rubro (`ActividadComercial`) que tenga al menos un comercio en estado `Firmado`. Las fotos se toman del campo `foto` del modelo `Comercio`. Los comercios sin foto no se muestran en la nube de logos de la card del rubro.
6. En el MVP, la gestión de comercios se realiza desde el admin técnico de Django.
7. La dirección es opcional: los emprendimientos sin local físico pueden publicarse y su detalle no muestra un bloque de dirección vacío.
8. La ficha modal se ofrece solamente desde el listado de una actividad
   comercial y su contenido parcial solo está disponible para comercios con
   estado `Firmado`. La página `/comercios/<pk>/` se conserva como destino
   indexable y compartible. Abrir o cerrar el modal no modifica la URL ni el
   historial del navegador.
