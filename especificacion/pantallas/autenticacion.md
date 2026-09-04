---
type: "Pantalla"
title: "Autenticación"
description: "Ingreso, cambio y recuperación de contraseña."
tags: [post-mvp, pantalla, usuarios, diseno-aprobado]
timestamp: 2026-09-03T00:00:00-03:00
---

# Autenticación

## Login

El formulario de ingreso conserva usuario y contraseña y agrega el acceso
`Olvidé mi contraseña`. Ese acceso se presenta como una acción secundaria con
texto gris oscuro, sin subrayado permanente, un ícono de llave, fondo suave en
hover y foco de teclado visible. No ofrece registro público.

## Cambiar contraseña

Pantalla autenticada accesible desde `Cuenta`. Solicita contraseña actual,
contraseña nueva y confirmación. Presenta los errores junto a cada campo y,
cuando finaliza, conserva la sesión y muestra una confirmación. La acción
principal `Guardar contraseña` usa el ícono `bi-key`.

## Recuperar contraseña

La solicitud pública pide DNI y email. La pantalla posterior siempre muestra
el mismo resultado neutro y no confirma si los datos existen, coinciden, están
limitados o pertenecen a una cuenta habilitada. Su título es `Solicitud
recibida` y explica que, por seguridad, no se informa si los datos coinciden;
solo si corresponden a una cuenta habilitada llegará el correo. `Enviar
instrucciones` usa `bi-envelope-arrow-up`.

El enlace del correo abre una pantalla para ingresar y confirmar una contraseña
nueva. Un enlace inválido, vencido o utilizado informa que ya no está
disponible y permite volver a solicitar otro. `Guardar contraseña` usa
`bi-key` y `Solicitar un enlace nuevo` usa `bi-envelope`. Después del cambio
correcto se ofrece ingresar a Uni2.

Todas las pantallas de autenticación y sus respuestas usan `no-store` y no se
incorporan al service worker ni a la navegación offline.
