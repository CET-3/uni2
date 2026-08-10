---
type: "Regla de negocio"
title: "Credenciales"
description: "Reglas de negocio sobre credenciales."
tags: [mvp, reglas]
timestamp: 2026-06-22T00:00:00-03:00
---

# Credenciales

## CREDENCIAL-001

Solo asociados activos poseen credenciales válidas.

## CREDENCIAL-002

La credencial debe validarse con un token UUID aleatorio. El QR codifica una
URL absoluta del entorno actual con la forma `/credenciales/<token UUID>/` y
no expone IDs internos, correlativos ni datos personales.

La pantalla autenticada del titular puede mostrar su DNI. Ese dato no forma
parte del QR ni de la copia guardada para usar sin conexión.

## CREDENCIAL-003

Si el token no existe o no es válido, debe mostrarse credencial inválida sin
revelar datos ni confirmar que una cuenta existe.

## CREDENCIAL-004

El comercio solo debe ver válida/inválida, nombre y apellido, tipo y estado. No debe ver deuda ni datos sensibles.

## CREDENCIAL-005

El asociado puede decidir guardar una copia mínima de su propia credencial en
un dispositivo para mostrarla sin conexión. La copia vence siete días después
de la última actualización online correcta.

## CREDENCIAL-006

Mostrar una copia offline no confirma vigencia. La validación del comercio
siempre requiere conexión y la respuesta actual del servidor.

## CREDENCIAL-007

La copia offline debe eliminarse al cerrar sesión, al cambiar de usuario, al
vencer o cuando el asociado elige quitarla. No debe incluir DNI, deuda, cuotas
ni información de sesión.

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
