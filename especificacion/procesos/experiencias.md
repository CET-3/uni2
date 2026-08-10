---
type: "Proceso"
title: "Experiencias externas"
description: "Procesos disponibles para asociados y comercios autenticados."
tags: [mvp, procesos, asociados, comercios]
timestamp: 2026-08-10T00:00:00-03:00
---

# Experiencias externas

## Cuenta y beneficios del asociado

**Responsable funcional:** grupo `Atención al asociado`. **Actor:** persona
vinculada a un `Asociado`; el grupo `Asociados` identifica su experiencia.

El asociado inicia sesión, consulta su credencial con DNI, vigencia y token,
revisa el estado de cuotas y accede a beneficios. Puede conservar la credencial
offline según las reglas de privacidad de la PWA.

**Casos de uso:** [ver credencial](../casos-de-uso/cu-ver-credencial.md),
[guardar credencial offline](../casos-de-uso/cu-guardar-credencial-offline.md) y
[ver estado de cuotas](../casos-de-uso/cu-ver-estado-cuotas.md).

## Operación del comercio adherido

**Responsable funcional:** grupo `Gestión de convenios`. **Actor:** persona
vinculada a un `Comercio`; el grupo `Comercios` identifica su experiencia.

El comercio inicia sesión y valida una credencial ingresando el DNI o el token.
El sistema informa la identidad y vigencia necesarias para aplicar el
beneficio, sin exponer información administrativa innecesaria.

**Caso de uso:** [validar credencial](../casos-de-uso/cu-validar-credencial.md).

Los grupos `Asociados` y `Comercios` no otorgan permisos de administración. La
experiencia efectiva depende además del vínculo con la entidad correspondiente.
