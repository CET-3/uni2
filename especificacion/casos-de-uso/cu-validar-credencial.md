---
type: "Caso de uso"
title: "CU-validar-credencial"
description: "Actor: Comercio"
tags: [mvp, caso-de-uso]
timestamp: 2026-06-22T00:00:00-03:00
---

# CU-validar-credencial

**Actor:** Comercio

**Flujo principal:**

1. Escanea el QR con la cámara común o ingresa el UUID o DNI manualmente.
2. El QR abre `/credenciales/<token UUID>/`.
3. Si no tiene sesión, inicia sesión y regresa a la URL escaneada.
4. El sistema comprueba el comercio vinculado y su convenio firmado.
5. Busca al asociado por `token_credencial` y verifica el estado actual.
6. Muestra válida o inválida y sólo los datos permitidos.

**Reglas relacionadas:** [Comercios — operación](../reglas/comercios-operacion.md), [Credenciales](../reglas/credenciales.md).

**Situaciones especiales:** URL o UUID inválido, asociado inactivo, comercio
sin convenio firmado, rol no admitido y ausencia de conexión.

**Modelos afectados:** Asociado, Comercio.
