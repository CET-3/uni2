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
3. El sistema responde siempre que, si los datos corresponden a una cuenta
   habilitada, recibirá un correo.
4. Cuando existe un asociado activo con usuario activo y ambos datos
   coinciden, registra y envía la comunicación `recuperacion_contrasena`.
5. La persona abre el enlace temporal recibido.
6. Ingresa y confirma una contraseña nueva.
7. El sistema guarda la contraseña, invalida el enlace y la dirige al login.

El email vigente de `Asociado` es la fuente de verdad. Se admite un envío por
cuenta dentro de una ventana inicialmente de 15 minutos. El enlace vence
inicialmente después de una hora. El token se genera mediante los mecanismos
firmados de Django y no se persiste en la comunicación, auditoría ni logs.

**Respuesta neutra:** datos inexistentes, email incorrecto, asociado sin email,
cuenta inactiva o límite alcanzado producen la misma presentación pública y no
revelan qué condición ocurrió.

**Situaciones especiales:** enlace vencido, alterado o ya utilizado; fallo del
backend de correo; varias cuentas que comparten email.

**Modelos afectados:** User, Asociado, Comunicacion y EntregaComunicacion.

**Reglas relacionadas:** [Usuarios](../reglas/usuarios.md) y
[Comunicaciones](../reglas/comunicaciones.md).
