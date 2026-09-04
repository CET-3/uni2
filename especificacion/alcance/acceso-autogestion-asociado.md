---
type: "Alcance"
title: "Etapa de acceso y autogestión del asociado"
description: "Alta de cuentas, contraseñas y edición de datos propios del asociado."
tags: [post-mvp, alcance, usuarios, asociados, diseno-aprobado]
timestamp: 2026-09-03T00:00:00-03:00
---

# Etapa de acceso y autogestión del asociado

Esta etapa completa el acceso digital del asociado después de su alta. Reutiliza
la infraestructura de correo transaccional y agrega recorridos acotados para
administrar la contraseña y los datos personales propios.

## Incluye

- Creación automática de un `User` al completar un alta individual, tanto
  manual como proveniente de una preinscripción.
- DNI como username y contraseña inicial.
- Correo individual `alta_usuario` cuando el asociado nuevo tiene email, con
  acceso al login e indicaciones sobre las credenciales iniciales.
- Cambio de contraseña para el asociado autenticado que conoce su contraseña
  actual.
- Recuperación de contraseña mediante DNI, email y un enlace temporal de un
  solo uso.
- Edición inmediata de nombre, apellido, teléfono, email y dirección por el
  propio asociado.
- Sincronización de nombre, apellido y email entre `Asociado` y su `User`.
- Auditoría explícita de los cambios de datos propios.

## Decisiones de seguridad y operación

- El email no es obligatorio. Sin email se crea igualmente el usuario con DNI
  como contraseña inicial, pero no se envía el correo de alta ni se puede usar
  la recuperación por correo.
- El formulario de recuperación pide DNI y email porque una dirección puede
  estar compartida por más de un asociado.
- Si DNI y email no corresponden a una cuenta activa, la recuperación lo
  informa explícitamente en el formulario. Esta decisión facilita la
  corrección de datos, aunque permite a terceros probar combinaciones y
  confirmar la existencia de cuentas.
- Una cuenta encontrada muestra la confirmación aunque una solicitud previa
  dentro de los últimos 15 minutos impida generar otro correo.
- El email vigente de `Asociado` es la fuente de verdad para recuperar la
  cuenta. Un cambio propio también actualiza `User.email`.
- Cargar un email después del alta no envía retroactivamente `alta_usuario`.
- Cada cuenta puede originar un solo correo de recuperación dentro de una
  ventana configurable, inicialmente de 15 minutos.
- El enlace de recuperación vence inicialmente después de una hora y deja de
  ser válido al cambiar la contraseña.
- Los tokens y contraseñas no se guardan en comunicaciones, auditoría ni logs.
- Un fallo de correo no revierte el alta ni una modificación de negocio.

## Protección de procesos masivos

La importación inicial del padrón y la acción `Crear usuarios faltantes` no
envían correos. El disparador de `alta_usuario` es explícito y está desactivado
por defecto; solamente las altas individuales manuales y por preinscripción lo
habilitan. Los importadores CSV, el admin técnico y las escrituras directas por
ORM tampoco lo habilitan implícitamente.

## Edición de datos propios

El asociado puede cambiar nombre, apellido, teléfono, email y dirección. Los
cambios se aplican inmediatamente y no requieren contraseña adicional,
confirmación por correo ni revisión de la Mutual. Nombre y apellido son
obligatorios; email, teléfono y dirección pueden quedar vacíos.

La pantalla y el service aceptan una lista cerrada. No permiten modificar DNI,
username, tipo, curso, clasificación, número de asociado, estado, cuotas ni
fechas, aunque se agreguen esos valores manualmente a la petición.

## No incluye

- Registro público o creación de cuentas sin un asociado previo.
- Verificación o confirmación de una dirección de email nueva.
- Correo posterior al cambio de contraseña o de datos personales.
- Correos de alta, invitaciones o recuperaciones por lote.
- Recuperación de cuentas de comercios o personal de gestión.
- Cambio de DNI o de datos institucionales por el propio asociado.
- Revisión de los cambios personales por parte de la Mutual.
- Endurecimiento general de las reglas de contraseña.

## Verificación esperada

Las pruebas deben cubrir los dos orígenes de alta individual, asociados sin
email, ausencia de envíos masivos, idempotencia, fallos del backend, respuestas
explícitas, límites de recuperación, tokens válidos e inválidos, cambio
autenticado, lista cerrada de datos propios, sincronización y auditoría.
