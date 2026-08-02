---
type: "Caso de uso"
title: "CU-instalar-Uni2"
description: "Actor: Persona que usa Uni2 desde un navegador compatible."
tags: [pwa, caso-de-uso, instalacion]
timestamp: 2026-08-01T00:00:00-03:00
---

# CU-instalar-Uni2

**Actor:** Visitante, Asociado, Comercio o Gestión.

**Precondición:** Abre Uni2 mediante HTTPS en un navegador compatible.

**Flujo principal:**

1. La persona navega normalmente por Uni2.
2. El navegador informa que la aplicación puede instalarse.
3. Uni2 ofrece una acción no invasiva “Instalar Uni2”.
4. La persona decide instalar.
5. El navegador confirma la instalación.
6. Uni2 aparece con su nombre e icono y abre en modo independiente desde `/`.

**Alternativas:**

- Si la sugerencia se descarta, Uni2 no insiste durante la misma navegación.
- En iOS se muestran instrucciones para “Agregar a pantalla de inicio”.
- Si el navegador no permite instalar, el sitio continúa sin errores ni
  controles inútiles.

**Reglas relacionadas:** [Progressive Web App](../reglas/pwa.md).

**Modelos afectados:** Ninguno.
