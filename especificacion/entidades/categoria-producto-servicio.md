---
type: "Entidad"
title: "CategoriaProductoServicio"
description: "Agrupa productos y servicios publicados por la mutual."
resource: "contenidos.models.CategoriaProductoServicio"
tags: [mvp, entidad]
timestamp: 2026-06-23T00:00:00-03:00
---

# CategoriaProductoServicio

Agrupa productos y servicios publicados por la mutual en el sitio público.

**Campos:**

- id*: identificador interno de la categoría.
- nombre*: nombre visible de la categoría.
- descripción: texto público que explica la categoría.
- etiqueta_icono: etiqueta textual para representar un ícono en la interfaz.
- texto_cta: texto libre de llamado a la acción. Puede incluir emails o URLs que la vista convierte en enlaces.
- imagen_informativa: imagen compartida por los productos de la categoría, por ejemplo una tabla de talles.
- título_imagen_informativa: título público que explica el contenido de la imagen informativa.
- activa*: indica si la categoría se publica en el sitio.
- orden*: posición usada para ordenar las categorías publicadas.

**Restricciones de datos:** el nombre de la categoría debe ser único. La imagen
informativa y su título se completan juntos; ninguno puede publicarse sin el
otro.

**Administración:** en el MVP se carga y edita desde el admin técnico de Django.

**Referencias funcionales:** ver [productos y servicios](../reglas/productos-servicios.md) y [CU-listar-productos-servicios-publicos](../casos-de-uso/cu-listar-productos-servicios-publicos.md).
