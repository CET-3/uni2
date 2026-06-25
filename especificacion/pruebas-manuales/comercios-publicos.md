---
type: "Prueba manual"
title: "Comercios públicos"
description: "Pruebas manuales para verificar el listado público de comercios."
tags: [mvp, prueba-manual]
timestamp: 2026-06-22T00:00:00-03:00
---

# Comercios públicos

Estas pruebas verifican que el sitio público muestre solamente los comercios
publicados y que respete el orden definido para publicación.

## Preparación

Desde el admin de Django, crear estos comercios:

1. Comercio A: estado `Firmado`, orden `2`.
2. Comercio B: estado `Firmado`, orden `1`.
3. Comercio C: estado `Pendiente`, orden `0`.
4. Comercio D: estado `Vencido`, orden `0`.
5. Comercio E: estado `Baja`, orden `0`.

Todos deben tener nombre, actividad comercial, beneficio, dirección y algún dato
público de contacto.

## Casos de prueba

### PM-COMERCIO-PUBLICO-001 - Abrir el listado público

**Pasos:**

1. Entrar al sitio público.
2. Abrir la sección `Comercios`.

**Resultado esperado:** la página carga correctamente.

### PM-COMERCIO-PUBLICO-002 - Mostrar solo comercios firmados

**Pasos:**

1. Abrir la sección `Comercios`.
2. Revisar los comercios visibles.

**Resultado esperado:** aparecen Comercio A y Comercio B. No aparecen Comercio
C, Comercio D ni Comercio E.

### PM-COMERCIO-PUBLICO-003 - Respetar el orden publicado

**Pasos:**

1. Abrir la sección `Comercios`.
2. Revisar el orden del listado.

**Resultado esperado:** Comercio B aparece antes que Comercio A, porque tiene
`orden = 1` y Comercio A tiene `orden = 2`.

### PM-COMERCIO-PUBLICO-004 - Cambiar el orden desde el admin

**Pasos:**

1. En el admin de Django, cambiar el orden de Comercio A a `0`.
2. Volver a abrir la sección `Comercios`.

**Resultado esperado:** Comercio A aparece antes que Comercio B.

### PM-COMERCIO-PUBLICO-005 - Publicar un comercio pendiente

**Pasos:**

1. En el admin de Django, cambiar Comercio C de `Pendiente` a `Firmado`.
2. Volver a abrir la sección `Comercios`.

**Resultado esperado:** Comercio C aparece en el listado público.

### PM-COMERCIO-PUBLICO-006 - Ocultar un comercio dado de baja

**Pasos:**

1. En el admin de Django, cambiar Comercio B de `Firmado` a `Baja`.
2. Volver a abrir la sección `Comercios`.

**Resultado esperado:** Comercio B deja de aparecer.

### PM-COMERCIO-PUBLICO-007 - Mostrar datos públicos

**Pasos:**

1. Abrir la sección `Comercios`.
2. Revisar la información visible de un comercio publicado.

**Resultado esperado:** se ve información pública como nombre, actividad
comercial, beneficio, dirección, teléfono, email o presencia web, si esos datos
fueron cargados.

### PM-COMERCIO-PUBLICO-008 - No mostrar datos internos

**Pasos:**

1. Abrir la sección `Comercios`.
2. Revisar la información visible de un comercio publicado.

**Resultado esperado:** no se ven notas internas, usuario asociado ni datos
administrativos que no correspondan a visitantes.

### PM-COMERCIO-PUBLICO-009 - Listado sin comercios publicados

**Pasos:**

1. En el admin de Django, dejar todos los comercios con un estado distinto de
   `Firmado`.
2. Volver a abrir la sección `Comercios`.

**Resultado esperado:** la página no se rompe y muestra un estado vacío claro.

### PM-COMERCIO-PUBLICO-010 - Revisar detalle de comercio pendiente

**Pasos:**

1. Ir a `/comercios/<pk>/` de un comercio con estado `Pendiente`.

**Resultado esperado:** no da error 404. Muestra "Este comercio estará disponible próximamente" con un enlace "Ver comercios adheridos".

### PM-COMERCIO-PUBLICO-011 - Revisar detalle de comercio firmado

**Pasos:**

1. Ir a `/comercios/<pk>/` de un comercio con estado `Firmado`.

**Resultado esperado:** se ven nombre, actividad comercial, dirección, beneficio y datos de contacto del comercio.

### PM-COMERCIO-PUBLICO-012 - Revisar en pantalla chica

**Pasos:**

1. Abrir la sección `Comercios`.
2. Achicar la ventana del navegador o probar desde un celular.

**Resultado esperado:** el listado sigue siendo legible y no se superponen
textos ni botones.
