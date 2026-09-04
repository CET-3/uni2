---
type: "Prueba manual"
title: "Acceso y autogestión del asociado"
description: "Alta de cuenta, contraseñas y actualización de datos propios."
tags: [post-mvp, pruebas-manuales, usuarios, asociados, comunicaciones]
timestamp: 2026-09-04T00:00:00-03:00
---

# Acceso y autogestión del asociado

Esta guía verifica los correos de acceso, el manejo de contraseñas y la edición
de datos personales. También comprueba que ningún proceso masivo envíe el
correo de alta.

## Preparación local

1. Actualizar el proyecto, aplicar migraciones y cargar los datos iniciales.
2. Levantar el servidor con `uv run python manage.py runserver`.
3. Mantener visible esa consola: el perfil local usa un backend que imprime
   allí los correos y no los envía a direcciones reales.
4. Ingresar con una cuenta que pueda crear asociados y gestionar solicitudes.
5. Preparar DNIs y emails ficticios que todavía no existan en la base local.

## Alta manual con email

1. Abrir `/gestion/asociados/nuevo/` y crear un asociado con email.
2. Confirmar que se crea un `User` vinculado cuyo username es el DNI y cuya
   contraseña inicial es también el DNI.
3. Buscar en Comunicaciones una única comunicación de tipo `alta_usuario` con
   destino igual al email del asociado.
4. Revisar el mensaje en la consola. Debe mostrar el DNI como usuario y
   contraseña inicial, enlazar a `/login/` y recomendar cambiar la contraseña.
5. Confirmar que el asunto no contiene nombre, DNI ni email.

## Alta manual sin email

1. Crear otro asociado dejando el email vacío.
2. Confirmar que el `User` se crea igualmente con DNI como username y
   contraseña inicial.
3. Confirmar que no se registra ninguna comunicación `alta_usuario` para ese
   asociado y no aparece un correo nuevo en la consola.

## Alta desde preinscripción

1. Crear y aprobar una preinscripción con email siguiendo la guía de
   [Preinscripción de asociados](preinscripcion-asociacion.md).
2. Ejecutar `Completar alta` una sola vez.
3. Confirmar que se crea el asociado con su `User`, se vincula la solicitud y
   se registra una única comunicación `alta_usuario`.
4. Verificar en la consola que el correo usa las credenciales DNI/DNI y el
   enlace al login.

## Procesos masivos sin correo

### Importación inicial

1. Importar una planilla de padrón que contenga al menos una fila con email.
2. Confirmar la importación.
3. Verificar que no se crea ninguna comunicación `alta_usuario` ni aparece un
   correo de alta en la consola.

### Crear usuarios faltantes

1. Elegir `Crear usuarios faltantes` después de la importación.
2. Completar todos los lotes si el proceso ofrece continuar.
3. Confirmar que los usuarios quedan vinculados con contraseña inicial DNI.
4. Verificar nuevamente que no se crea `alta_usuario` y no sale ningún correo.

La misma exclusión se espera del importador CSV, el admin técnico y las
escrituras directas por ORM.

## Cambio de contraseña autenticado

1. Ingresar como asociado y abrir `Cambiar contraseña` desde Cuenta.
2. Intentar guardar usando una contraseña actual incorrecta. Debe mostrar el
   error y conservar la contraseña vigente.
3. Repetir con la contraseña actual correcta y una contraseña nueva válida.
4. Confirmar el mensaje de éxito y navegar a otra pantalla sin volver a
   iniciar sesión.
5. Cerrar sesión. La contraseña inicial debe ser rechazada y la nueva debe
   permitir el ingreso.
6. Confirmar que este cambio no genera correo.

## Recuperación por DNI y email

1. Desde `/login/`, elegir `Olvidé mi contraseña`.
2. Enviar primero un DNI inexistente y un email ficticio. La respuesta debe
   indicar solamente que se enviará un correo si corresponde a una cuenta
   habilitada.
3. Repetir con el DNI correcto y un email incorrecto. La respuesta visible debe
   ser idéntica.
4. Enviar el DNI y email vigentes de un asociado activo. Debe registrarse una
   comunicación `recuperacion_contrasena` y aparecer un correo en la consola.
5. Volver a solicitarlo antes de 15 minutos. Debe mostrarse la misma respuesta
   pública y no crearse otra comunicación.
6. Abrir el enlace del primer correo, elegir una contraseña nueva y confirmar
   que permite ingresar.
7. Volver a abrir el enlace usado. Debe indicar que ya no está disponible.
8. Alterar manualmente un carácter de otro token. Debe mostrar el mismo estado
   no disponible.
9. Para comprobar el vencimiento de una hora de forma reproducible, ejecutar
   `uv run pytest usuarios/tests/test_password_recovery.py -q`; la prueba
   controla el reloj del generador sin cambiar la hora del equipo.

Un asociado inactivo, un usuario inactivo o una cuenta sin email deben recibir
la misma respuesta pública y no originar una comunicación.

## Mis datos

1. Ingresar como asociado y abrir `Mis datos` desde Cuenta.
2. Confirmar que aparecen únicamente nombre, apellido, teléfono, email y
   dirección con sus valores actuales.
3. Cambiar los cinco campos y guardar. El cambio debe verse inmediatamente.
4. Verificar en el admin técnico que `User.first_name`, `User.last_name` y
   `User.email` quedaron sincronizados.
5. Revisar Auditoría: debe existir un evento de modificación con el usuario
   asociado como actor, origen `Asociado` y antes/después de cada campo.
6. Dejar teléfono, email y dirección vacíos. Debe permitirse; la pantalla
   advierte que sin email no se reciben correos ni se puede recuperar la clave.
7. Intentar nombre vacío, email inválido y teléfono inválido. Cada dato debe
   mostrar su error y no guardarse.
8. Confirmar que agregar o cambiar el email no envía un `alta_usuario`
   retroactivo ni otro correo.

Los tests automatizados publican además DNI, tipo, estado y número de asociado
manipulados y comprueban que la lista cerrada los ignore.

## Correo real redirigido en staging

1. Usar solamente `UNI2_STAGING_TRANSACTIONAL_EMAIL_MODE=redirect`, nunca
   `enabled`, siguiendo la preparación de
   [Preinscripción de asociados](preinscripcion-asociacion.md#correo-real-redirigido-en-staging).
2. Ejecutar un alta individual y una recuperación con datos ficticios.
3. Confirmar que cada `EntregaComunicacion` conserva como destino el email
   ficticio original.
4. Confirmar que ambos mensajes llegan únicamente a la casilla segura y que el
   asunto comienza con `[STAGING]`.
5. Confirmar que los enlaces usan `https://uni2-staging.vercel.app/`.

## Privacidad y PWA

1. Consultar `Mis datos`, `Cambiar contraseña` y las cuatro pantallas de
   recuperación.
2. En las herramientas del navegador, verificar `Cache-Control` con `private`
   y `no-store`, y ausencia de `X-Uni2-PWA-Cacheable: public`.
3. En la pantalla que contiene el token, verificar
   `Referrer-Policy: same-origin`.
4. Desconectar la red e intentar abrir esas rutas desde una ventana nueva. No
   deben estar disponibles en el caché público de la PWA.
