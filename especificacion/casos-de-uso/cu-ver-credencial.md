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
5. Calcula su vigencia para la fecha actual y muestra `Credencial activa` o
   `Credencial inactiva`.
6. Muestra el tipo y el dato institucional: curso para un asociado o
   clasificación para un adherente.

La pantalla de credencial muestra únicamente el estado calculado y no informa
la causa de una inactividad ni agrega acciones de cobro. El asociado consulta
cuotas y deuda desde `Mis cuotas`.

Si el asociado abre la URL del QR, el servidor compara primero el token con el
de su perfil. Una URL ajena se rechaza sin confirmar si existe.

Con conexión, el asociado puede elegir guardar una copia mínima durante siete
días mediante
[CU-guardar-credencial-offline](cu-guardar-credencial-offline.md). Esa copia
no reemplaza la validación online del comercio.

La copia offline guarda `Activa` o `Inactiva` tal como se calculó al
actualizarla, junto con nombre, tipo y el dato institucional visible. No
almacena la causa, DNI, cuotas ni importes.

**Reglas relacionadas:** [Credenciales](../reglas/credenciales.md).

**Modelos afectados:** Asociado, Usuario.
