---
type: "Caso de uso"
title: "CU-administrar-convenios"
description: "Actor: Gestión de convenios."
tags: [mvp, caso-de-uso, convenios]
timestamp: 2026-08-10T00:00:00-03:00
---

# CU-administrar-convenios

**Actor:** usuario del grupo `Gestión de convenios`.

1. Entra al admin técnico desde la home.
2. Consulta o crea la actividad comercial necesaria.
3. Crea o modifica el comercio, beneficio, estado y datos del convenio.
4. Guarda y verifica el resultado en el sitio público cuando corresponde.

**Resultado:** comercio y convenio actualizados con evento de auditoría.

**Permisos:** consulta, alta y modificación de actividades y comercios. No
incluye borrado, contenidos, asociados, usuarios ni auditoría general.

**Pruebas:** alta válida; edición; dato obligatorio ausente; intento de editar
una publicidad; usuario sin el grupo.
