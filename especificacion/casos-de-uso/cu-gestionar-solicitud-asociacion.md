---
type: "Caso de uso"
title: "CU-gestionar-solicitud-asociacion"
description: "Actor: Atención al asociado o Administrador de la mutual con permisos explícitos."
tags: [post-mvp, caso-de-uso, diseno-aprobado]
timestamp: 2026-08-26T00:00:00-03:00
---

# CU-gestionar-solicitud-asociacion

**Actor:** Atención al asociado o Administrador de la mutual con los permisos
correspondientes a la acción.

**Flujo de consulta:**

1. Ingresa a `Solicitudes de asociación` desde la experiencia administrativa.
2. Ve una lista con búsqueda, filtros por estado, tipo y fecha y cantidad de
   resultados. Puede consultar todas las abiertas, todas incluyendo finales o
   un estado concreto.
3. Abre la ficha de una solicitud.
4. Consulta datos, estado, historial y entregas de correo relacionadas.

**Revisión:**

1. Desde una solicitud `recibida`, elige aprobar datos, observar o cancelar.
2. Observar exige una explicación, cambia a `observada` y envía el enlace de corrección.
3. Aprobar cambia a `datos_aprobados` y avisa que la persona debe acercarse.
4. Cancelar exige confirmación y motivo, cambia a `cancelada` y comunica el cierre.
5. Desde `datos_aprobados` puede volver a observar o cancelar si aparece un problema.

**Finalización presencial:**

1. La persona se presenta en la Mutual con su solicitud en `datos_aprobados`.
2. El personal revisa un resumen y elige `Completar alta`.
3. El sistema vuelve a validar DNI, curso o clasificación y el estado actual.
4. En una única transacción crea el asociado con las reglas vigentes, genera
   sus cuotas iniciales, lo vincula y cambia la solicitud a `alta_completada`.
5. Continúa en el detalle operativo del asociado creado.
6. Si vuelve a la solicitud completada, puede abrir desde allí la ficha del
   asociado generado.

**Errores y concurrencia:**

- Si otra persona cambió el estado, se rechaza la acción y se muestra la ficha actualizada.
- Si el DNI fue incorporado al padrón por otro flujo, no completa el alta.
- Si curso o clasificación dejaron de estar activos, no completa el alta y la
  solicitud debe observarse.
- Un doble envío no crea dos asociados.
- Un fallo de correo no revierte la transición funcional y puede reenviarse.

**Reglas relacionadas:** [Solicitudes de asociación](../reglas/solicitudes-asociacion.md),
[Altas de asociado](../reglas/altas-de-asociado.md),
[Comunicaciones](../reglas/comunicaciones.md) y
[Trazabilidad](../reglas/trazabilidad.md).

**Modelos afectados:** SolicitudAsociacion, Asociado, Curso,
ClasificacionAdherente, PeríodoCuota, Cuota, Comunicacion,
EntregaComunicacion, EventoAuditoria.
