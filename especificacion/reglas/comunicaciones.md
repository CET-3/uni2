---
type: "Regla de negocio"
title: "Comunicaciones"
description: "Reglas comunes para mensajes y entregas por correo o canales futuros."
tags: [post-mvp, reglas, diseno-aprobado]
timestamp: 2026-09-03T00:00:00-03:00
---

# Comunicaciones

## COMUNICACION-001 — Mensaje y entrega

Una comunicación representa el mensaje originado por un hecho de negocio. Una
entrega representa cada intento de hacerlo llegar a un destino mediante un
canal. Esta separación permite que un evento futuro use varios canales o llegue
a muchas personas sin duplicar su regla de origen.

## COMUNICACION-002 — Tipos, alcance y canales

Cada comunicación usa un tipo estable y declara alcance `individual` o `lote`.
El correo transaccional de preinscripción es individual. Los avisos futuros de
cuotas generadas serán comunicaciones operativas obligatorias por lote.
Notificaciones push, campañas promocionales y procesamiento por lote no se
implementan en esta etapa.

Ser masiva no convierte una comunicación en promocional: el alcance y el
propósito son conceptos distintos. Las reglas de consentimiento para
promociones se definirán cuando ese caso de uso sea diseñado. Esta etapa no
incorpora preferencias de comunicación.

## COMUNICACION-003 — Destinatarios

Una entrega no depende de que exista un `User`: puede dirigirse al correo de
una solicitud. El destino se toma del estado confirmado del objeto de negocio
al crear la entrega.

## COMUNICACION-004 — Idempotencia

Cada comunicación tiene una clave de idempotencia. Repetir una petición o una
operación de negocio no crea dos avisos equivalentes. Un reenvío solicitado por
un operador sí crea una entrega nueva y queda distinguido en el historial.

## COMUNICACION-005 — Transacciones y fallos

La operación de negocio se confirma antes de intentar el envío. Un fallo del
proveedor no revierte una preinscripción, observación, aprobación o cancelación.
La entrega queda `fallida`, con información operativa acotada, y puede
reenviarse. El reenvío manual requiere `gestion.reenviar_comunicaciones`,
capacidad asignada inicialmente a Atención al asociado y Administrador de la
mutual. Los fallos no se ocultan ni se presentan como mensajes enviados.

## COMUNICACION-006 — Contenido y privacidad

Las plantillas HTML y texto plano se versionan en el repositorio. El registro
no guarda contraseñas, tokens, el cuerpo completo ni datos personales que no
sean necesarios para operar la entrega. El asunto no expone DNI, deuda u otra
información sensible.

Los enlaces privados se generan para la entrega y no se copian en auditoría ni
logs. Un reenvío genera un enlace nuevo.

## COMUNICACION-007 — Ambientes

Cada clase de canal tiene un modo explícito. Desarrollo y tests capturan los
mensajes. Staging no envía a los destinos originales: omite los correos por
defecto y sólo permite SMTP real mediante el modo `redirect`, con una casilla
segura obligatoria y un prefijo visible en el asunto. Producción sólo habilita
el proveedor real cuando toda la configuración requerida está presente, no
admite `redirect` y una configuración incompleta no cae silenciosamente en un
backend inseguro.

## COMUNICACION-008 — Correos de preinscripción

La primera etapa incluye:

- solicitud recibida, con enlace de seguimiento;
- solicitud observada, con explicación y enlace de corrección;
- correcciones recibidas;
- datos aprobados, con indicaciones para finalizar presencialmente;
- solicitud cancelada, con el motivo.

El correo posterior al alta del asociado queda fuera de este alcance porque
debe diseñarse también para las altas sin preinscripción.

## COMUNICACION-009 — Evolución por lote y push

Una comunicación por lote agrupará entregas por destinatario, permitirá
procesar tandas, medir avance, reintentar solo fallos y usar claves de
idempotencia por destinatario y canal. La generación de cuotas no deberá
esperar el envío de esos avisos.

El canal push tendrá suscripciones y permisos por dispositivo y evitará datos
privados en el contenido visible de una pantalla bloqueada. Estas capacidades
se documentan como evolución y no crean modelos vacíos ni comportamiento
simulado en la primera implementación.
