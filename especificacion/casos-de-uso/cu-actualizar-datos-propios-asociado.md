---
type: "Caso de uso"
title: "CU-actualizar-datos-propios-asociado"
description: "Actor: asociado autenticado que actualiza sus datos personales."
tags: [post-mvp, caso-de-uso, asociados, autogestion, diseno-aprobado]
timestamp: 2026-09-03T00:00:00-03:00
---

# CU-actualizar-datos-propios-asociado

**Actor:** asociado autenticado con un `Asociado` vinculado.

**Flujo principal:**

1. Abre `Mis datos` desde el menú de su cuenta.
2. Consulta y modifica nombre, apellido, teléfono, email o dirección.
3. El sistema valida la lista cerrada de campos y sus formatos.
4. Aplica los cambios inmediatamente.
5. Sincroniza nombre, apellido y email en el `User` vinculado.
6. Registra el antes y el después en auditoría, identificando al propio usuario
   y el origen Asociado.
7. Muestra la confirmación y los datos actualizados.

Nombre y apellido son obligatorios. Email, teléfono y dirección pueden quedar
vacíos. Al dejar el email vacío se advierte que no estarán disponibles el
correo transaccional ni la recuperación de contraseña.

No se solicita nuevamente la contraseña y no se envía un correo de
confirmación. El email nuevo, si existe, queda disponible inmediatamente para
la recuperación.

**Campos no modificables:** DNI, username, tipo, curso, clasificación, número
de asociado, estado, fechas, cuotas y cualquier otro dato no enumerado. Una
petición manipulada no cambia esos valores.

**Situaciones especiales:** cuenta sin asociado vinculado, asociado inactivo,
nombre o apellido vacío, email inválido, teléfono inválido y petición con
campos no autorizados.

**Modelos afectados:** Asociado, User y EventoAuditoria.

**Reglas relacionadas:** [Asociados](../reglas/asociados.md),
[Usuarios](../reglas/usuarios.md) y [Trazabilidad](../reglas/trazabilidad.md).
