---
type: "Caso de uso"
title: "CU-usar-Uni2-sin-conexion"
description: "Actor: Persona que pierde conectividad mientras usa Uni2."
tags: [pwa, caso-de-uso, offline]
timestamp: 2026-08-01T00:00:00-03:00
---

# CU-usar-Uni2-sin-conexion

**Actor:** Visitante, Asociado, Comercio o Gestión.

**Flujo principal:**

1. La persona abre una página con conexión.
2. Uni2 guarda solamente recursos comunes y contenido público permitido.
3. La conexión se pierde.
4. Uni2 informa el estado sin interrumpir la navegación.
5. Una página pública ya visitada puede mostrar su última copia segura.
6. Para otra navegación se muestra la pantalla sin conexión.
7. Al recuperar la red, Uni2 informa que volvió a estar online y las
   operaciones nuevas vuelven a usar el servidor.

**Restricciones:**

- No se muestra información autenticada desde el caché general.
- No se guardan ni reenvían formularios.
- La credencial tiene un flujo privado separado.

**Reglas relacionadas:** [Progressive Web App](../reglas/pwa.md).

**Modelos afectados:** Ninguno.
