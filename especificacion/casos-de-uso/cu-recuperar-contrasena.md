---
type: "Caso de uso"
title: "CU-recuperar-contrasena"
description: "Actor: asociado que no puede ingresar y tiene un email registrado."
tags: [post-mvp, caso-de-uso, usuarios, comunicaciones, diseno-aprobado]
timestamp: 2026-09-03T00:00:00-03:00
---

# CU-recuperar-contrasena

**Actor:** asociado que no puede ingresar y tiene un email registrado.

**Flujo principal:**

1. Desde el login elige `Olvidé mi contraseña`.
2. Ingresa su DNI y email.
3. Si no existe un asociado activo con usuario activo y coincidencia de ambos
   datos, el formulario informa `No encontramos una cuenta activa con ese DNI
   y email. Revisá los datos ingresados.`
4. Cuando la cuenta existe, registra y envía la comunicación
   `recuperacion_contrasena` y muestra `Solicitud recibida`. Si ya se originó
   una comunicación dentro de la ventana de 15 minutos, muestra igualmente la
   confirmación pero no genera otra. Esa pantalla sólo se habilita para el
   siguiente acceso después de validar la solicitud; abrir su URL directamente
   vuelve al formulario.
5. La persona abre el enlace temporal recibido.
6. Ingresa y confirma una contraseña nueva.
7. El sistema guarda la contraseña, invalida el enlace y la dirige al login.

El email vigente de `Asociado` es la fuente de verdad. Se admite un envío por
cuenta dentro de una ventana inicialmente de 15 minutos. El enlace vence
inicialmente después de una hora. El token se genera mediante los mecanismos
firmados de Django y no se persiste en la comunicación, auditoría ni logs.

**Respuesta explícita:** datos inexistentes, email incorrecto, asociado sin
email o cuenta inactiva muestran el mismo error de cuenta no encontrada. La
decisión prioriza que la persona pueda corregir sus datos y acepta que la
coincidencia de una cuenta quede expuesta.

**Situaciones especiales:** enlace vencido, alterado o ya utilizado; fallo del
backend de correo; varias cuentas que comparten email.

**Modelos afectados:** User, Asociado, Comunicacion y EntregaComunicacion.

**Reglas relacionadas:** [Usuarios](../reglas/usuarios.md) y
[Comunicaciones](../reglas/comunicaciones.md).
