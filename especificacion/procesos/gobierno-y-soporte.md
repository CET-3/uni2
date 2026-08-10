---
type: "Proceso"
title: "Usuarios, accesos, auditoría y supervisión"
description: "Procesos de gobierno de la operación sin mezclar responsabilidades."
tags: [mvp, procesos, permisos, auditoria]
timestamp: 2026-08-10T00:00:00-03:00
---

# Usuarios, accesos, auditoría y supervisión

## Usuarios y accesos

**Responsable:** grupo `Administrador de permisos`.

Da de alta cuentas, actualiza sus datos y asigna grupos existentes. Puede
consultar la definición de grupos, pero no modificarla, elevar cuentas a
superusuario ni asignar `Administrador de la app`. Los grupos se acumulan por
responsabilidad.

**Caso de uso:** [administrar usuarios y accesos](../casos-de-uso/cu-administrar-usuarios-accesos.md).

## Auditoría y supervisión

**Responsables:** `Administrador de permisos` y `Administrador de la mutual`
pueden consultar la auditoría general. `Atención al asociado` ve solamente los
movimientos contextuales habilitados desde la ficha.

La auditoría permite reconstruir actor, acción, entidad, objeto, cambios y
operación relacionada. Es de solo lectura y no reemplaza los controles de
permiso del proceso que originó cada evento.

**Caso de uso:** [consultar auditoría](../casos-de-uso/cu-consultar-auditoria.md).
