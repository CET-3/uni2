---
type: "Caso de uso"
title: "CU-listar-comercios-publicos"
description: "Actor: Visitante"
tags: [mvp, caso-de-uso]
timestamp: 2026-06-22T00:00:00-03:00
status: "listo"
---

# CU-listar-comercios-publicos

**Actor:** Visitante

**Flujo principal:**

1.  Ingresa a la home.
2.  Selecciona `Comercios` en la navegación y el sistema lo ubica en `/#beneficios`.
3.  El sistema muestra los rubros que tienen comercios publicados y sus beneficios vigentes.
4.  Dentro del detalle de un rubro, selecciona un comercio firmado y el sistema
    abre su ficha pública en un modal, sin recargar la página ni cambiar la URL.
5.  Puede cerrar el modal para continuar en el rubro o abrir la ficha completa
    mediante `/comercios/<pk>/`.
6.  Desde una publicidad, un enlace compartido o una navegación sin JavaScript,
    abre directamente la página completa del comercio.
7.  El visitante puede consultar los datos públicos de contacto o presencia web disponibles.
8.  Desde una publicidad o un enlace público, el visitante puede abrir el detalle de un comercio. Si el comercio está `Firmado`, ve sus datos completos. Si no lo está, ve una pantalla informativa "Este comercio estará disponible próximamente".

La ruta `/comercios/` se conserva por compatibilidad, pero no forma parte de la navegación principal.

**Reglas relacionadas:** [Comercios públicos](../reglas/comercios-publicos.md).

**Modelos afectados:** ActividadComercial, Comercio.
