---
type: "Regla de negocio"
title: "Credenciales"
description: "Reglas de negocio sobre credenciales."
tags: [mvp, reglas]
timestamp: 2026-06-22T00:00:00-03:00
---

# Credenciales

## CREDENCIAL-001

El estado operativo de la credencial se calcula al consultarla y no se almacena
en `Asociado`. Una baja administrativa o una deuda exigible la inactivan. Si el
asociado permanece de alta y cancela toda la deuda exigible, la credencial
vuelve a estar activa automáticamente en la siguiente consulta.

La exigibilidad para credenciales se determina por mes: hasta el día 10
inclusive la cuota del mes actual no bloquea; desde el 11 sí puede hacerlo.
Las cuotas futuras no bloquean. El [tablero de Métricas](metricas.md#metricas-007--credenciales-vigentes-hoy)
usa esta misma regla para contar credenciales, independientemente de sus filtros históricos.

La credencial informa solamente el estado resultante. No expone la causa de la
inactividad ni incorpora acciones de cobro; deuda y cuotas se consultan en su
pantalla específica.

## CREDENCIAL-002

La credencial debe validarse con un token UUID aleatorio. El QR codifica una
URL absoluta del entorno actual con la forma `/credenciales/<token UUID>/` y
no expone IDs internos, correlativos ni datos personales.

La pantalla autenticada del titular y el resultado de validación de un comercio
habilitado pueden mostrar el DNI. Ese dato no forma parte del QR ni de la copia
guardada para usar sin conexión.

## CREDENCIAL-003

Si el token no existe o no es válido, debe mostrarse credencial inválida sin
revelar datos ni confirmar que una cuenta existe.

## CREDENCIAL-004

El comercio solo debe ver nombre y apellido, DNI, tipo, el dato institucional
correspondiente —curso o clasificación— y `Credencial activa` o
`Credencial inactiva`. No debe conocer si la inactividad proviene de una baja o
de deuda, ni ver cuotas, importes u otros datos sensibles. Un identificador
inexistente se informa como `Credencial inválida`.

## CREDENCIAL-005

El asociado puede decidir guardar una copia mínima de su propia credencial en
un dispositivo para mostrarla sin conexión. La copia vence siete días después
de la última actualización online correcta.

## CREDENCIAL-006

Mostrar una copia offline no confirma vigencia. La validación del comercio
siempre requiere conexión y la respuesta actual del servidor.

## CREDENCIAL-007

La copia offline debe eliminarse al cerrar sesión, al cambiar de usuario, al
vencer o cuando el asociado elige quitarla. Puede incluir nombre, tipo y el
dato institucional visible —curso o clasificación—. No debe incluir DNI,
deuda, cuotas ni información de sesión.

## CREDENCIAL-008

La URL identifica una credencial, pero no concede acceso. Una persona sin
sesión debe autenticarse y regresar a la misma URL antes de que el servidor
decida qué experiencia puede usar.

## CREDENCIAL-009

Un asociado sólo puede resolver el token exacto de su propia credencial. Un
token ajeno se rechaza con una respuesta genérica.

## CREDENCIAL-010

Un comercio sólo puede resolver y validar una credencial cuando está
autenticado, vinculado a ese usuario y su convenio está firmado. Se conserva
el ingreso manual del UUID o del DNI como alternativa. El DNI se envía dentro
del formulario y no se incorpora a la URL ni al QR.

## CREDENCIAL-011

Las respuestas asociadas a la URL de una credencial son privadas, no se
almacenan en caché y no envían la URL completa como referente a otros orígenes.
La aplicación no copia el UUID en auditoría ni mensajes de error.

## CREDENCIAL-012

Un usuario sin una experiencia de asociado propietario o comercio habilitado
recibe acceso denegado. Los permisos se comprueban siempre en el servidor.
