---
type: "Entidad"
title: "ActividadComercial"
description: "Clasifica el rubro o actividad principal de un comercio adherido."
resource: "comercios.models.ActividadComercial"
tags: [mvp, modelo-de-datos]
timestamp: 2026-07-29T00:00:00-03:00
status: "listo"
---

# ActividadComercial

Clasifica el rubro o actividad principal de un comercio adherido.

**Campos:**

- id\*: identificador interno de la actividad comercial.
- nombre\*: nombre del rubro o actividad principal del comercio.
- descripción: texto público opcional que presenta el rubro en su página de beneficios.

**Administración:** en el MVP se carga y edita desde el admin técnico de Django. El nombre abre el formulario de edición desde el listado y la descripción puede dejarse vacía; en ese caso la página pública usa un texto genérico.
