---
type: "Caso de uso"
title: "CU-administrar-publicidades"
description: "Actor: Gestión de publicidades."
tags: [mvp, caso-de-uso, publicidades]
timestamp: 2026-08-10T00:00:00-03:00
---

# CU-administrar-publicidades

**Actor:** usuario del grupo `Gestión de publicidades`.

1. Entra al admin técnico y abre Publicidades.
2. Crea o modifica texto, imagen, vigencia, orden y destino.
3. Si corresponde, selecciona un producto/servicio o comercio existente.
4. Guarda y revisa su presentación pública.

**Resultado:** publicidad actualizada con evento de auditoría.

**Permisos:** publicidades en consulta, alta y modificación; productos y
comercios solo en consulta para vincular. No incluye borrado.

**Pruebas:** publicidad sin vínculo; vínculo a producto; vínculo a comercio;
vigencia; intento de editar el objeto vinculado; usuario sin el grupo.
