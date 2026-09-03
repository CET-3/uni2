---
type: "Arquitectura"
title: "Comunicaciones"
description: "Separación de eventos, mensajes y entregas por correo y canales futuros."
tags: [post-mvp, arquitectura, diseno-aprobado]
timestamp: 2026-09-03T00:00:00-03:00
---

# Comunicaciones

La app `comunicaciones` concentra infraestructura compartida por los dominios
sin apropiarse de sus reglas. `asociados` decide cuándo una solicitud fue
observada; `comunicaciones` compone, registra e intenta entregar el aviso.

## Separación de responsabilidades

- El dominio de origen confirma primero su operación.
- Un tipo estable identifica qué debe comunicarse.
- `Comunicacion` representa el mensaje lógico y su origen.
- `EntregaComunicacion` representa cada destino y canal.
- Las plantillas HTML y texto plano viven versionadas en
  `templates/comunicaciones/email/`.
- Los adaptadores de canal aíslan la API pública del proveedor concreto.
- Las vistas no llaman directamente a `send_mail()` ni conocen credenciales del proveedor.

## API de aplicación

Los dominios solicitan una comunicación mediante un service explícito con tipo,
origen, destinatario y clave de idempotencia. No se usan signals implícitos para
decidir mensajes de negocio. El intento de entrega comienza después del commit
de la operación de origen.

La primera implementación procesa correos individuales. Conserva las entregas
fallidas y permite un reenvío manual. Una etapa posterior podrá incorporar un
procesador programado o una cola que consuma la misma interfaz; la aplicación
no depende de que exista un worker permanente en Vercel.

## Ambientes

Los settings separados `UNI2_TRANSACTIONAL_EMAIL_MODE`,
`UNI2_BATCH_EMAIL_MODE` y `UNI2_WEB_PUSH_MODE` continúan siendo barreras
independientes.

- Local y tests usan captura o memoria.
- Staging omite el correo transaccional por defecto. Puede probar el backend
  SMTP solamente en modo `redirect`, que conserva el destino original en la
  entrega pero envía a una única casilla segura y marca el asunto con
  `[STAGING]`.
- Staging mantiene deshabilitados el correo por lote y push.
- Producción falla de forma explícita al habilitar un canal sin su
  configuración completa y no admite el modo `redirect`.

El proveedor real de correo queda detrás de la configuración estándar y del
adaptador. Remitente, `Reply-To`, SPF, DKIM y DMARC forman parte de la puesta en
marcha productiva y no se escriben como secretos en el repositorio.
La cuenta inicial, los modos y la configuración de staging se detallan en
[Correo transaccional](correo-transaccional.md).

## Seguridad y observabilidad

- No se guardan cuerpos completos, contraseñas ni tokens privados.
- Los asuntos evitan datos sensibles.
- Se registran estado, intentos, fechas, error acotado e identificador del proveedor.
- Los permisos para consultar, reenviar y, en el futuro, iniciar lotes son capacidades separadas.
- Los lotes futuros se procesan por destinatario, con idempotencia y avance, sin
  bloquear la operación de negocio que los originó.
- Push tendrá suscripciones por dispositivo y no incluirá datos privados en la
  notificación visible.

## Primer uso

La preinscripción incorpora los primeros correos transaccionales. Recuperación
de contraseña, correo posterior al alta, avisos obligatorios de cuotas por lote,
comunicados institucionales, promociones y push reutilizarán esta frontera,
pero cada caso deberá definir sus propias reglas antes de implementarse.
