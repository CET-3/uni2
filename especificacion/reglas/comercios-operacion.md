---
type: "Regla de negocio"
title: "Comercios operación"
description: "Reglas de negocio sobre el uso del sistema por parte de comercios."
tags: [mvp, reglas]
timestamp: 2026-06-22T00:00:00-03:00
---

# Comercios operación

Estas reglas describen qué puede hacer un comercio autenticado dentro del
sistema.

## COMERCIO-OPERACION-001

Solo comercios con estado firmado pueden validar credenciales.

## COMERCIO-OPERACION-002

Un usuario con rol Comercio y un comercio vinculado puede consultar los datos
de su propio comercio y convenio en todos sus estados. El vínculo se resuelve
desde el usuario autenticado y no mediante un identificador recibido en la URL.
La consulta es de solo lectura y no habilita acceso al admin técnico.
