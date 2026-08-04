---
type: "Caso de uso"
title: "CU-consultar-auditoria"
description: "Actor: Gestión con permiso para ver auditoría."
tags: [mvp, caso-de-uso, diseno-aprobado, pendiente]
timestamp: 2026-08-01T00:00:00-03:00
---

# CU-consultar-auditoria

**Estado:** aprobado y pendiente de implementación.

**Actor:** Gestión con permiso `gestion.ver_auditoria`.

**Flujo principal:**

1. La persona ingresa a Auditoría desde gestión.
2. El sistema muestra los eventos más recientes.
3. La persona filtra por fecha, actor, acción, entidad, origen u objeto.
4. El sistema conserva el orden cronológico descendente y pagina los
   resultados.
5. La persona abre un evento u operación.
6. El sistema muestra los campos modificados, valores anteriores y nuevos,
   motivo y eventos relacionados por `operacion_id`.
7. Si el objeto sigue disponible y la persona tiene permiso, puede ir a su
   pantalla de detalle.

**Permisos:** requiere `gestion.ver_auditoria`. El permiso es independiente de
consultar o editar asociados y de las acciones de baja o anulación.

**Situaciones especiales:** evento de proceso automático, usuario desactivado,
objeto eliminado excepcionalmente, valor protegido, dato anterior a la
auditoría, operación con varios eventos y búsqueda sin resultados.

**Modelos afectados:** `EventoAuditoria` en modo de solo lectura.

**Referencias:** [reglas de trazabilidad](../reglas/trazabilidad.md) y
[pantalla de auditoría](../pantallas/auditoria.md).

