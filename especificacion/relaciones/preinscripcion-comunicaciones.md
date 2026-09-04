---
type: "Relación"
title: "Relaciones de preinscripción y comunicaciones"
description: "Relaciones incorporadas después del MVP para solicitudes y entregas."
tags: [post-mvp, modelo-de-datos, diseno-aprobado]
timestamp: 2026-08-26T00:00:00-03:00
---

# Relaciones de preinscripción y comunicaciones

- Curso 1 - N SolicitudAsociacion como curso_actual
- ClasificacionAdherente 1 - N SolicitudAsociacion
- Asociado 0..1 - 0..1 SolicitudAsociacion como alta originada en preinscripción
- SolicitudAsociacion 1 - N EventoAuditoria mediante referencia estructurada de auditoría
- SolicitudAsociacion 1 - N Comunicacion como origen
- Comunicacion 1 - N EntregaComunicacion

`SolicitudAsociacion` no hereda relaciones operativas de `Asociado`. Antes del
alta no tiene cuotas, pagos, credencial ni usuario.
