---
type: "Caso de uso"
title: "CU-consultar-sitio-publico"
description: "Actor: Visitante"
tags: [mvp, caso-de-uso]
timestamp: 2026-06-22T00:00:00-03:00
status: "listo"
---

# CU-consultar-sitio-publico

**Actor:** Visitante

**Flujo principal:**

1. El visitante ingresa a la home del sitio.
2. Ve una sección de **Servicios** con las categorías de productos y servicios disponibles. Puede entrar al detalle de cada categoría.
3. Ve una sección de **Beneficios** con los rubros de comercios adheridos que tienen al menos un comercio firmado con foto. Puede entrar al detalle de cada rubro.
4. Ve una sección **Nuestros favoritos** con las publicidades activas. Cada publicidad puede tener un enlace al detalle de un comercio o producto. Solo se muestran publicidades vinculadas a comercios con estado `Firmado`.
5. Ve una sección **Cómo asociarse** con los pasos para ser parte de UNI2, la cuota social tomada del período actual —o del último anterior cuando no hay período del mes— y los horarios de atención.
6. Puede navegar al login para acceder como asociado o comercio.

La navegación superior lleva directamente a las secciones `#productos-servicios` y `#beneficios` de esta misma home. En mobile cierra el menú antes de desplazar para mantener visibles los títulos debajo de la barra sticky.

**Casos de uso relacionados:** [CU-listar-productos-servicios-publicos](cu-listar-productos-servicios-publicos.md), [CU-listar-comercios-publicos](cu-listar-comercios-publicos.md).

**Modelos afectados:** Publicidad, ProductoServicio, ActividadComercial, Comercio.
