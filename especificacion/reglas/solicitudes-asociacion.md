---
type: "Regla de negocio"
title: "Solicitudes de asociación"
description: "Reglas de preinscripción, revisión y conversión en asociado."
tags: [post-mvp, reglas, diseno-aprobado]
timestamp: 2026-08-26T00:00:00-03:00
---

# Solicitudes de asociación

## SOLICITUD-ASOCIACION-001 — Separación del padrón

Una solicitud no es un asociado. Antes de `alta_completada` no recibe número,
credencial, cuotas ni usuario y no aparece en consultas del padrón.

## SOLICITUD-ASOCIACION-002 — Tipo derivado

El formulario pregunta `¿Sos estudiante del CET 3?`. Una respuesta afirmativa
determina tipo `asociado` y exige un curso activo. Una respuesta negativa
determina tipo `adherente` y exige una clasificación de adherente activa. La
persona no elige directamente entre los términos internos Asociado y Adherente.

## SOLICITUD-ASOCIACION-003 — Datos y validaciones

Nombre, apellido, DNI o documento, correo, teléfono, domicilio y condición
respecto del CET 3 son obligatorios.

- Nombre y apellido admiten letras Unicode, espacios, apóstrofes y guiones, no números.
- `dni` conserva un único campo para DNI o documento extranjero. Admite entre
  5 y 20 caracteres alfanuméricos; espacios, puntos y guiones de entrada se
  normalizan para comparar duplicados.
- El correo debe tener formato válido, pero puede repetirse entre personas.
- El teléfono admite dígitos, espacios, `+`, guiones y paréntesis y debe
  contener entre 8 y 15 dígitos reales.
- El domicilio no puede quedar vacío.
- Todas las reglas se validan en el servidor.

## SOLICITUD-ASOCIACION-004 — Duplicados

El DNI normalizado es el control de identidad. No se crea una solicitud si ya
existe un asociado o una solicitud no cancelada con ese valor. Una solicitud
cancelada no impide una presentación nueva. La respuesta pública no expone
datos ni el estado de una persona existente.

## SOLICITUD-ASOCIACION-005 — Estados

El flujo normal es:

`recibida → observada → recibida → datos_aprobados → alta_completada`.

Desde `recibida` se puede pasar a `observada`, `datos_aprobados` o `cancelada`.
Desde `observada`, la persona puede reenviar y volver a `recibida`, o el
personal puede cancelar. Desde `datos_aprobados` se puede volver a `observada`,
completar el alta o cancelar. `alta_completada` y `cancelada` son estados finales.

## SOLICITUD-ASOCIACION-006 — Correcciones

La persona puede modificar sus datos solamente cuando la solicitud está
`observada` y mediante el último enlace privado vigente. Al reenviar, vuelve a
`recibida`. El personal no corrige silenciosamente los datos declarados: puede
observar, aprobar, cancelar o completar el alta.

Toda observación exige una explicación visible para la persona. Toda
cancelación exige motivo. Cambios de estado, correcciones y responsables quedan
en el historial de auditoría; una corrección pública se identifica como acción
de la persona mediante enlace privado, no como un usuario interno ficticio.

## SOLICITUD-ASOCIACION-007 — Enlace privado

No existe búsqueda pública por DNI, correo o número de solicitud. El token es
aleatorio y solo se persiste mediante un resumen seguro. Emitir un nuevo enlace
invalida el anterior. El vencimiento es configurable y un usuario autorizado
puede emitir otro sin cambiar el estado.

El enlace vence a los 30 días; el plazo queda como setting explícito para poder
ajustarlo sin cambiar el flujo. La página permite consultar el estado mientras esté vigente,
pero muestra el formulario editable únicamente en `observada`. Sus respuestas
usan `noindex` y `no-store`.

## SOLICITUD-ASOCIACION-008 — Protección contra abuso

Además de CSRF, la creación pública admite hasta 30 intentos por dirección IP
en una ventana de 10 minutos. Una solicitud observada admite hasta cinco
reenvíos de correcciones por hora. Superar el límite no crea registros ni
correos y muestra un mensaje específico para que la persona espere antes de
reintentar. Cuando el documento puede corresponder a un asociado o a otra
solicitud se muestra en cambio un mensaje prudente y accionable, sin confirmar
qué registro existe ni exponer su estado. Los límites son settings explícitos y
no reemplazan las restricciones de duplicidad.

La clave del límite es un resumen HMAC de una dirección IP validada. En local
se usa `REMOTE_ADDR`; dentro de Vercel se admite exclusivamente
`X-Vercel-Forwarded-For`, con `REMOTE_ADDR` como fallback. No se confía en un
`X-Forwarded-For` genérico. Los contadores viven en la base compartida y cada
consumo elimina las ventanas anteriores vencidas de esa misma acción.

## SOLICITUD-ASOCIACION-009 — Alta presencial

`datos_aprobados` significa que la revisión terminó y que la persona debe
acercarse a la Mutual. No representa aprobación definitiva, pago ni pertenencia
al padrón.

La denominación visible de este estado es `Datos aprobados`. El flujo no usa
`Documentación aprobada` porque la preinscripción no recibe archivos ni exige
presentar documentación digital. El correo correspondiente tiene como asunto
`Los datos de tu preinscripción fueron aprobados`, confirma que se revisaron y
aprobaron los datos declarados, e indica que todavía falta acercarse a la Mutual
para completar el alta. Tampoco se lo denomina `Preinscripción aprobada`, para
no dar a entender que el alta ya fue completada.

Completar el alta es una operación atómica e idempotente: crea el asociado con
las reglas vigentes, genera sus cuotas iniciales, lo vincula a la solicitud y
cambia el estado a `alta_completada`. Si una parte falla, no queda un alta
parcial y la solicitud permanece en `datos_aprobados`.

Esta etapa no registra ni comprueba un pago de asociación. Tampoco rediseña la
creación de usuarios ni el correo posterior al alta, que deberán resolverse
para altas con y sin preinscripción.

## SOLICITUD-ASOCIACION-010 — Permisos

Las capacidades son `gestion.consultar_solicitudes_asociacion`,
`gestion.revisar_solicitudes_asociacion`,
`gestion.completar_solicitudes_asociacion` y
`gestion.cancelar_solicitudes_asociacion`. El reenvío de una comunicación usa
la capacidad transversal `gestion.reenviar_comunicaciones`. Atención al
asociado y Administrador de la mutual reciben las cinco. Las acciones se
controlan también en el servidor y quedan auditadas.

## SOLICITUD-ASOCIACION-011 — Conservación

Las solicitudes completadas o canceladas y su historial se conservan. Esta
etapa no incorpora anonimización ni eliminación automática.
