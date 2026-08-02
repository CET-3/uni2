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

## CREDENCIAL-005

El asociado puede decidir guardar una copia mínima de su propia credencial en
un dispositivo para mostrarla sin conexión. La copia vence siete días después
de la última actualización online correcta.

## CREDENCIAL-006

Mostrar una copia offline no confirma vigencia. La validación del comercio
siempre requiere conexión y la respuesta actual del servidor.

## CREDENCIAL-007

La copia offline debe eliminarse al cerrar sesión, al cambiar de usuario, al
vencer o cuando el asociado elige quitarla. No debe incluir DNI, deuda, cuotas
ni información de sesión.
