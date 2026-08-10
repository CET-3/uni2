---
type: "Caso de uso"
title: "CU-consultar-auditoria"
description: "Actor: Gestión con permiso para ver auditoría."
tags: [mvp, caso-de-uso, implementado]
timestamp: 2026-08-09T00:00:00-03:00
---

# CU-consultar-auditoria

**Estado:** implementado.

**Actor:** Gestión con permiso `gestion.ver_auditoria`.

**Flujo principal:**

1. La persona ingresa a Auditoría desde gestión.
2. El sistema muestra los eventos más recientes.
3. La persona filtra por fecha, actor, acción, entidad, origen u objeto.
4. El sistema agrupa los eventos que comparten `operacion_id`, conserva el
   orden cronológico descendente y pagina por operaciones.
5. El sistema muestra directamente todos los eventos de cada operación, con
   sus campos modificados, valores anteriores y nuevos y motivo.
6. Si un filtro coincide con un evento de una operación compuesta, el sistema
   incluye también los demás eventos relacionados para no recortar el
   historial de esa operación.
7. Si el objeto sigue disponible y la persona tiene permiso, puede ir a su
   pantalla de detalle.

**Permisos:** requiere `gestion.ver_auditoria`. El permiso es independiente de
consultar o editar asociados y de las acciones de baja o anulación.

**Acceso temporal:** la auditoría general continúa disponible desde la home administrativa. El acceso filtrado por asociado fue retirado del detalle; la ruta y sus filtros se conservan para un recorrido futuro.

**Situaciones especiales:** evento de proceso automático, usuario desactivado,
objeto eliminado excepcionalmente, valor protegido, dato anterior a la
auditoría, operación con varios eventos y búsqueda sin resultados.

**Modelos afectados:** `EventoAuditoria` en modo de solo lectura.

**Referencias:** [reglas de trazabilidad](../reglas/trazabilidad.md) y
[pantalla de auditoría](../pantallas/auditoria.md).
