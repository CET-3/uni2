---
type: "Regla de negocio"
title: "Credenciales"
description: "Reglas de negocio sobre credenciales."
tags: [mvp, reglas]
timestamp: 2026-06-22T00:00:00-03:00
---

# Credenciales

## CREDENCIAL-001

Solo asociados activos poseen credenciales válidas.

## CREDENCIAL-002

La credencial debe validarse con un token UUID aleatorio y no debe exponer IDs internos ni correlativos en URLs o QR.

## CREDENCIAL-003

Si el token no existe o no es valido, debe mostrarse credencial inválida.

## CREDENCIAL-004

El comercio solo debe ver válida/inválida, nombre y apellido, tipo y estado. No debe ver deuda ni datos sensibles.
