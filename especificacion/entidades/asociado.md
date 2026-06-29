---
type: "Entidad"
title: "Asociado"
description: "Representa a una persona asociada o adherente a la mutual."
resource: "asociados.models.Asociado"
tags: [mvp, modelo-de-datos]
timestamp: 2026-06-22T00:00:00-03:00
---

# Asociado

Representa a una persona asociada o adherente a la mutual.

**Campos:**

- id\*
- usuario
- nombre\*
- apellido\*
- dni\*
- email
- teléfono
- dirección
- tipo\*
- número_asociado
- token_credencial\*
- curso_actual
- estado\*
- fecha_alta\*
- fecha_inicio_cobro\*
- fecha_baja
- motivo_baja

**Tipos:** asociado, adherente.

**Estados:** activo, inactivo.

**Restricciones de datos:** DNI único, número automático, token UUID único, usuario opcional.

**Admin técnico:** la selección de `usuario` debe usar búsqueda/autocompletado para soportar muchos usuarios y evitar combos largos.

**Referencias funcionales:** ver [reglas de asociados](../reglas/asociados.md), [altas de asociado](../reglas/altas-de-asociado.md), [credenciales](../reglas/credenciales.md) y [usuarios](../reglas/usuarios.md).
