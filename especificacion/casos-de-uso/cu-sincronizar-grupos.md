---
type: "Caso de uso"
title: "CU-sincronizar-grupos"
description: "Actor: Administrador de la app."
tags: [mvp, caso-de-uso, operacion, permisos]
timestamp: 2026-08-10T00:00:00-03:00
---

# CU-sincronizar-grupos

**Actor:** responsable técnica con acceso al ambiente y rol `Administrador de
la app`.

1. Ejecuta `python manage.py sincronizar_grupos` para revisar diferencias.
2. Revisa grupos faltantes, permisos diferentes y usuarios cuyo `is_staff` no
   coincide con la capacidad de admin.
3. Ejecuta `python manage.py sincronizar_grupos --apply`.
4. Ejecuta `python manage.py sincronizar_grupos --check` para confirmar.

**Resultado:** los grupos administrados por Uni2 coinciden exactamente con la
matriz versionada. Ejecutarlo nuevamente no produce cambios.

**Restricción:** el comando no decide integrantes. Las asignaciones de personas
se realizan por el caso de uso de usuarios y accesos.
