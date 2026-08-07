---
type: "Caso de uso"
title: "CU-guardar-credencial-offline"
description: "Actor: Asociado autenticado."
tags: [pwa, caso-de-uso, credencial, offline]
timestamp: 2026-08-01T00:00:00-03:00
---

# CU-guardar-credencial-offline

**Actor:** Asociado autenticado.

**Precondición:** Tiene conexión, una credencial vigente y usa un dispositivo
que considera seguro.

**Flujo principal:**

1. Entra a Mi credencial.
2. Uni2 explica qué datos se guardarán, que durarán siete días y que cerrar
   sesión los eliminará.
3. El asociado elige “Guardar en este dispositivo”.
4. Uni2 guarda una representación mínima y confirma la fecha de vencimiento.
5. Sin conexión, el asociado entra a Mi credencial.
6. Uni2 muestra la copia, la fecha de última actualización y el aviso de que
   el comercio debe validar su vigencia online.
7. Al volver la conexión, una visita correcta a la credencial puede renovar
   la copia y su plazo cuando se conserva el consentimiento.

**Alternativas:**

- “Quitar de este dispositivo” elimina la copia inmediatamente.
- Cerrar sesión elimina la copia.
- Iniciar con otra cuenta elimina cualquier copia que no le pertenezca.
- Una copia vencida no se muestra.
- Si nunca se aceptó guardarla, la vista offline explica que no existe una
  credencial disponible.

**Reglas relacionadas:** [Credenciales](../reglas/credenciales.md) y
[Progressive Web App](../reglas/pwa.md).

**Modelos afectados:** Asociado y Usuario solamente como fuente online; no se
crea persistencia nueva en el servidor.
