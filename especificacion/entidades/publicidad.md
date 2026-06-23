---
type: "Entidad"
title: "Publicidad"
description: "Card destacada para la home pública."
resource: "contenidos.models.Publicidad"
tags: [mvp, entidad]
timestamp: 2026-06-23T00:00:00-03:00
---

# Publicidad

Card destacada para la sección `Nuestros favoritos` de la home pública.

**Campos:**

- id*: identificador interno de la publicidad.
- título*: título visible de la card.
- descripción*: texto breve que acompaña la publicidad.
- etiqueta_principal*: etiqueta superior, por ejemplo `Alimentos`, `Librería` o `Servicio`.
- etiqueta_secundaria*: texto destacado, por ejemplo `10% OFF`, `Nuevo` o `Disponible`.
- foto: imagen horizontal opcional usada como fondo de la card.
- producto_servicio: producto o servicio vinculado, si la publicidad apunta a un detalle de producto o servicio.
- comercio: comercio vinculado, si la publicidad apunta a un detalle de comercio.
- activa*: indica si se muestra en la home.
- orden*: posición usada para ordenar las publicidades.

**Restricciones de datos:** puede estar vinculada a un producto o servicio, o a un comercio, pero no a ambos al mismo tiempo. También puede no tener vínculo; en ese caso se muestra sin enlace.

**Formato recomendado de foto:** horizontal 16:9, tamaño recomendado `1600 x 900 px`, mínimo `1100 x 620 px`, formato WebP recomendado o JPG aceptado, peso ideal menor a 500 KB. La imagen se recorta con cobertura completa de la card, por eso el contenido importante debe quedar centrado.

**Administración:** en el MVP se carga y edita desde el admin técnico de Django.

**Referencias funcionales:** ver [publicidades](../reglas/publicidades.md) y [sitio público](../pantallas/sitio-publico.md).
