---
type: "Caso de uso"
title: "CU-desplegar-version"
description: "Actor: Responsable técnica autorizada."
tags: [mvp, caso-de-uso, despliegue, operacion]
timestamp: 2026-08-10T00:00:00-03:00
---

# CU-desplegar-version

**Actor:** responsable técnica autorizada.

**Precondiciones:** el cambio está versionado en una rama, la especificación
está actualizada y las pruebas automáticas pasan.

**Flujo principal:**

1. Abre un PR hacia `staging` y revisa los checks.
2. Si existen migraciones, revisa el plan y las aplica explícitamente sobre la
   base de staging antes de actualizar el sitio.
3. Integra el PR y verifica el despliegue, readiness y pruebas acordadas en el
   dominio estable de staging.
4. Abre el PR de promoción desde `staging` hacia `main`.
5. Repite el control y aplica previamente las migraciones compatibles sobre
   Producción cuando corresponda.
6. Integra el PR para iniciar el despliegue productivo automático.
7. Verifica el sitio, la versión desplegada y los controles posteriores.
8. Vuelve a integrar `main` en `staging` para conservar las ramas alineadas.

**Situaciones especiales:** check fallido, rama desactualizada, migración
incompatible, readiness fallido, smoke test fallido y necesidad de rollback.

**Resultado:** la misma versión aprobada en staging queda publicada y
verificada en Producción.

**Reglas relacionadas:** [Despliegue en Vercel](../arquitectura/despliegue.md)
y [Entorno de staging](../arquitectura/staging.md).
