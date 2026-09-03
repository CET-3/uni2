---
type: "Prueba manual"
title: "Preinscripción de asociados"
description: "Recorrido de verificación del formulario público y su gestión interna."
tags: [post-mvp, pruebas-manuales]
timestamp: 2026-09-03T00:00:00-03:00
---

# Preinscripción de asociados

Esta guía verifica el recorrido incorporado en esta etapa. No comprueba pagos
online, notificaciones push ni el correo posterior al alta porque todavía no
forman parte del alcance.

## Preparación

1. Usar un ambiente con cursos y clasificaciones de adherente activos.
2. Ingresar también con una cuenta de `Atención al asociado` o `Administrador
   de la mutual`.
3. Verificar que `.env` tenga `UNI2_TRANSACTIONAL_EMAIL_MODE=enabled`. En
   desarrollo, consultar los correos impresos por la consola; el backend local
   no usa SMTP ni envía a direcciones reales. En tests se capturan en memoria.

## Correo real redirigido en staging

1. Desplegar primero con `UNI2_STAGING_TRANSACTIONAL_EMAIL_MODE=disabled`.
2. Configurar las variables `UNI2_STAGING_SITE_URL`,
   `UNI2_STAGING_DEFAULT_FROM_EMAIL`, `UNI2_STAGING_EMAIL_REDIRECT_TO`,
   `UNI2_STAGING_EMAIL_HOST`, `UNI2_STAGING_EMAIL_PORT`,
   `UNI2_STAGING_EMAIL_HOST_USER`, `UNI2_STAGING_EMAIL_HOST_PASSWORD` y
   `UNI2_STAGING_EMAIL_USE_TLS` en el proyecto Vercel `uni2-staging`. La
   contraseña de aplicación sólo se pega en el almacén de secretos de Vercel.
3. Usar `UNI2_STAGING_TRANSACTIONAL_EMAIL_MODE=redirect` y volver a desplegar.
   Staging no admite `enabled`.
4. Crear una solicitud con datos inequívocamente ficticios y una dirección de
   destino distinta de la casilla segura.
5. Confirmar que `EntregaComunicacion` conserva el destino ficticio original,
   pero el mensaje llega únicamente a `uni2.app.cet3@gmail.com` y su asunto
   comienza con `[STAGING]`.
6. Confirmar que el enlace del mensaje comienza con
   `https://uni2-staging.vercel.app/` y abre la solicitud en staging.
7. Observar la solicitud, enviar una corrección y ejecutar `Reenviar
   comunicación`; todos los mensajes deben conservar la misma redirección.
8. Ante un problema, volver el modo a `disabled` y desplegar. Si existe riesgo
   de exposición, revocar además la contraseña de aplicación
   `UNI2 Staging Vercel` desde Google.

## Presentación pública

1. Desde la home, comprobar que `Comenzar preinscripción` abre `/sumate/`.
2. Elegir que la persona es estudiante del CET 3. Verificar que se muestre y
   exija curso, y que la solicitud resultante sea de tipo asociado.
3. Repetir con una persona que no estudia en el CET 3. Verificar que se muestre
   y exija una clasificación, y que la solicitud resulte adherente.
4. Probar un documento con letras, como un documento extranjero, y confirmar
   que el único campo `DNI o documento` lo acepte.
5. Intentar enviar campos vacíos, nombres con números, correo inválido y teléfono
   demasiado corto. Los errores deben aparecer junto al campo y en el resumen.
6. Enviar una solicitud válida. Debe aparecer una confirmación neutra, sin datos
   personales, y registrarse la comunicación `Solicitud recibida`.
7. Repetir el mismo documento con puntos, espacios o guiones. No debe crearse
   otra solicitud ni revelarse información sobre la existente.

## Revisión y corrección

1. Abrir `Solicitudes de asociación` desde la experiencia administrativa. La
   vista inicial debe mostrar solicitudes abiertas, con las más antiguas primero.
2. Abrir la solicitud y elegir `Observar`. La explicación es obligatoria.
3. Abrir el último enlace privado generado. Debe mostrar el formulario con la
   explicación y permitir corregirlo; el enlace anterior debe quedar inválido.
4. Enviar la corrección. La solicitud debe volver a `Recibida`, mostrar una
   confirmación y registrar el correo de correcciones recibidas.
5. Aprobar los datos. El estado visible debe ser `Datos aprobados` y el correo
   debe confirmar la aprobación de los datos e indicar que falta finalizar
   presencialmente.
6. Si una entrega queda fallida, usar `Reenviar comunicación`. Debe registrarse
   un intento nuevo sin repetir la transición de estado.

## Cierres posibles

1. Desde una solicitud con datos aprobados, confirmar `Completar alta`.
   Debe crear un único asociado con sus cuotas iniciales, vincular la solicitud,
   cambiarla a `Alta completada` y abrir el detalle del asociado.
2. Confirmar que esta acción no registra un pago y no envía correo de bienvenida.
3. Con otra solicitud abierta, elegir `Cancelar solicitud`. El motivo es
   obligatorio y el estado `Cancelada` es definitivo.
4. Presentar una solicitud nueva con el documento de la cancelada. Debe estar
   permitida; una solicitud activa o un asociado existente deben impedirla.

## Privacidad y permisos

1. Confirmar que formulario, resultados y seguimiento respondan con `no-store`
   y `X-Robots-Tag: noindex, nofollow`.
2. Un token inválido o vencido debe mostrar un mensaje neutro, sin indicar si
   existe una solicitud.
3. Una cuenta sin permisos no puede consultar ni ejecutar acciones sobre las
   solicitudes aunque conozca las URLs.
