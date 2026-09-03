---
type: "Arquitectura"
title: "Correo transaccional"
description: "Diseño del envío SMTP de preinscripciones en staging y Producción."
tags: [post-mvp, arquitectura, comunicaciones, diseno-aprobado]
timestamp: 2026-09-03T00:00:00-03:00
---

# Correo transaccional

Este documento define cómo Uni2 enviará los correos individuales de
preinscripción mediante SMTP sin permitir que staging contacte por accidente a
las direcciones guardadas en su base.

## Cuenta institucional inicial

La primera puesta en marcha usará la cuenta gratuita de Gmail
`uni2.app.cet3@gmail.com`, con el remitente visible
`UNI2 App — Mutual CET 3`.

La cuenta pertenece a la Mutual y no a una persona particular. Debe conservar
recuperación documentada, verificación en dos pasos y una contraseña principal
única. Uni2 no recibe esa contraseña: cada ambiente usa una contraseña de
aplicación diferente, almacenada únicamente como secreto de Vercel. Esto
permite revocar el acceso de staging sin interrumpir Producción y viceversa.

Mientras no exista una casilla institucional bajo dominio propio, el campo
`From` debe usar la misma dirección `uni2.app.cet3@gmail.com`. No debe aparentar
un remitente `@uni2.app` que la cuenta gratuita no puede autenticar.

La cuenta gratuita admite hasta 500 envíos diarios según la documentación de
Gmail revisada el 3 de septiembre de 2026. Este valor se incorporará al futuro
inventario de servicios externos y deberá revisarse periódicamente:

- <https://support.google.com/mail/answer/22839>
- <https://support.google.com/accounts/answer/185833>

## Modos de entrega

`UNI2_TRANSACTIONAL_EMAIL_MODE` representa el comportamiento efectivo del
servicio y admite estos modos internos:

- `disabled`: registra la entrega como omitida y no abre una conexión SMTP;
- `redirect`: envía por SMTP, pero sustituye el destinatario por una casilla de
  prueba obligatoria y agrega `[STAGING]` al asunto;
- `enabled`: envía al destinatario original registrado por el dominio.

Cada ambiente restringe qué modos puede usar:

| Ambiente | Modos permitidos | Valor inicial |
| --- | --- | --- |
| Desarrollo | `disabled`, `enabled` con backend de consola | `enabled` |
| Tests | el definido por cada prueba con backend en memoria | `disabled` |
| Staging | `disabled`, `redirect` | `disabled` |
| Producción | `disabled`, `enabled` | `disabled` |

Staging nunca acepta `enabled` y Producción nunca acepta `redirect`. La
separación evita que una variable copiada entre proyectos elimine la barrera de
seguridad.

## Configuración de staging

Staging usa variables con prefijo propio y no hereda las credenciales SMTP de
Producción. Para activar `redirect` deben estar presentes:

| Variable | Clasificación | Propósito |
| --- | --- | --- |
| `UNI2_STAGING_TRANSACTIONAL_EMAIL_MODE` | No secreto | `disabled` o `redirect`. |
| `UNI2_STAGING_SITE_URL` | No secreto | Origen estable para los enlaces privados de prueba. |
| `UNI2_STAGING_DEFAULT_FROM_EMAIL` | No secreto | Remitente visible con la dirección Gmail institucional. |
| `UNI2_STAGING_EMAIL_REDIRECT_TO` | Sensible | Único destinatario autorizado en staging. |
| `UNI2_STAGING_EMAIL_HOST` | No secreto | Servidor SMTP; inicialmente `smtp.gmail.com`. |
| `UNI2_STAGING_EMAIL_PORT` | No secreto | Puerto SMTP; inicialmente `587`. |
| `UNI2_STAGING_EMAIL_HOST_USER` | Sensible | `uni2.app.cet3@gmail.com`. |
| `UNI2_STAGING_EMAIL_HOST_PASSWORD` | Secreto | Contraseña de aplicación exclusiva de staging. |
| `UNI2_STAGING_EMAIL_USE_TLS` | No secreto | TLS; por defecto `true`. |

El primer destinatario seguro será la misma cuenta institucional:
`uni2.app.cet3@gmail.com`.

Si el modo es `redirect` y falta una variable obligatoria, staging no debe
iniciar. Si el modo es `disabled`, conserva el backend ficticio y no exige
credenciales.

## Flujo de una entrega redirigida

1. El dominio confirma la preinscripción o su cambio de estado.
2. `comunicaciones` crea la comunicación y registra como destino la dirección
   original de la solicitud.
3. Después del commit, el servicio detecta el modo `redirect`.
4. El mensaje conserva sus plantillas HTML y texto, sustituye el destinatario
   SMTP por `UNI2_STAGING_EMAIL_REDIRECT_TO` y antepone `[STAGING]` al asunto.
5. Los enlaces privados se construyen con `UNI2_STAGING_SITE_URL` y apuntan al
   ambiente de staging.
6. La entrega queda `enviada` o `fallida` según la respuesta del backend.

La sustitución se realiza únicamente en la frontera SMTP. El destino original
permanece en `EntregaComunicacion` para verificar la regla de negocio, pero
nunca se pasa al backend de correo en staging. Un reenvío manual atraviesa la
misma frontera y no puede evitar la redirección.

El asunto no incluye la dirección original, DNI ni otros datos personales. La
casilla receptora consulta el detalle de la entrega en Uni2 cuando necesita
comparar el mensaje con su origen.

## Fallos y recuperación

Un error de autenticación, conectividad, cuota o rechazo SMTP no revierte la
operación de negocio. La entrega queda `fallida`, incrementa sus intentos y
guarda solamente un error operativo acotado. Nunca se registran contraseñas de
aplicación, cuerpos completos ni enlaces privados.

Para detener los envíos se cambia el modo de staging a `disabled` y se vuelve a
desplegar. Ante una posible exposición también se revoca la contraseña de
aplicación `UNI2 Staging Vercel` desde la cuenta de Google. Producción utilizará
otra contraseña de aplicación y no depende de ese secreto.

## Verificación requerida

La implementación debe probar automáticamente que:

- staging continúa desactivado por defecto;
- el intento de usar `enabled` en staging es rechazado;
- `redirect` exige toda su configuración y una dirección de redirección válida;
- la entrega conserva el destino original, pero el backend recibe únicamente
  el destinatario seguro;
- el asunto de staging incluye el prefijo y no incluye el destino original;
- los reenvíos manuales también se redirigen;
- las fallas siguen registrándose sin alterar la operación de origen;
- Producción conserva solamente `disabled` y `enabled`.

La prueba manual comienza con datos ficticios, confirma la recepción en
`uni2.app.cet3@gmail.com`, abre el enlace sobre staging y recorre al menos una
observación, una corrección y un reenvío. Producción permanece desactivada hasta
que este recorrido sea aceptado.

## Fuera de alcance

Esta puesta en marcha no incorpora colas, envíos por lote, campañas,
notificaciones push, un dominio de correo propio ni monitoreo automático de la
cuota de Gmail. Esas capacidades requieren decisiones independientes.
