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

1.  Escanea el QR o ingresa el token.
2.  El sistema busca al asociado por `token_credencial`.
3.  Verifica el estado.
4.  Muestra el resultado.

**Reglas relacionadas:** [COMERCIO-OPERACION-001](../reglas/comercios-operacion.md#comercio-operacion-001), [CREDENCIAL-001](../reglas/credenciales.md#credencial-001), [CREDENCIAL-002](../reglas/credenciales.md#credencial-002), [CREDENCIAL-003](../reglas/credenciales.md#credencial-003), [CREDENCIAL-004](../reglas/credenciales.md#credencial-004).

**Situaciones especiales:** QR invalido, asociado inactivo, comercio inactivo.

**Modelos afectados:** Asociado, Comercio.
