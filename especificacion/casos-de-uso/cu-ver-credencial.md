---
type: "Caso de uso"
title: "CU-ver-credencial"
description: "Actor: Asociado"
tags: [mvp, caso-de-uso]
timestamp: 2026-06-22T00:00:00-03:00
---

# CU-ver-credencial

**Actor:** Asociado

**Flujo principal:**

1.  Inicia sesión.
2.  Entra a Mi Credencial.
3. Construye una URL absoluta del entorno para el token propio.
4. Muestra la credencial digital con un QR que contiene esa URL y conserva el
   UUID escrito como respaldo.

Si el asociado abre la URL del QR, el servidor compara primero el token con el
de su perfil. Una URL ajena se rechaza sin confirmar si existe.

Con conexión, el asociado puede elegir guardar una copia mínima durante siete
días mediante
[CU-guardar-credencial-offline](cu-guardar-credencial-offline.md). Esa copia
no reemplaza la validación online del comercio.

**Reglas relacionadas:** [Credenciales](../reglas/credenciales.md).

**Modelos afectados:** Asociado, Usuario.
