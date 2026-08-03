---
type: "Prueba manual"
title: "Progressive Web App"
description: "Matriz manual de instalación, offline, privacidad, actualización y rollback."
tags: [pwa, pruebas, mobile, privacidad]
timestamp: 2026-08-01T00:00:00-03:00
---

# Pruebas manuales de la PWA

Usar staging HTTPS. Las pruebas con evidencia compartida y las que recorren dos
identidades se hacen con `qa-asociado-a`, `qa-asociado-b` y `qa-comercio`, los
perfiles ficticios creados durante el endurecimiento. Cuando staging contiene
una copia de Producción, limitarse a esas cuentas y al admin QA autorizado: no
descargar listados ni registrar capturas con datos personales.

## Matriz mínima

| Entorno | Instalación | Offline | Credencial | Actualización |
|---|---:|---:|---:|---:|
| Chrome Android actual | Obligatoria | Obligatoria | Obligatoria | Obligatoria |
| Safari iOS/iPadOS agregado a inicio | Obligatoria | Obligatoria | Obligatoria | Obligatoria |
| Chrome o Edge desktop | Obligatoria | Obligatoria | Obligatoria | Obligatoria |
| Safari macOS | Cuando esté disponible | Obligatoria | Obligatoria | Obligatoria |
| Navegador sin instalación | Degradación normal | Según soporte | Online normal | Sin errores |

La emulación de WebKit en CI no reemplaza la prueba en un iPhone o iPad real.

## Instalación e identidad

1. Abrir staging por HTTPS.
2. Verificar nombre `UNI2 STG`, icono con insignia `STG`, color naranja e
   inicio `/`.
3. Instalar desde la acción disponible.
4. Abrir desde el launcher y confirmar modo independiente.
5. Probar icono normal y `maskable`.
6. Descartar una sugerencia y comprobar que no reaparece insistentemente.
7. En iOS seguir las instrucciones de “Agregar a pantalla de inicio”.

## Navegación sin conexión

1. Visitar una página pública.
2. Pasar a modo avión y volver a esa página: debe aparecer la copia pública.
3. Abrir una página pública nunca visitada: debe aparecer “Sin conexión”.
4. Confirmar que CSS, fuentes, logos e iconos siguen disponibles.
5. Abrir cuotas, gestión, admin y login: no debe aparecer contenido
   autenticado viejo.
6. Recuperar la red y comprobar el aviso de conexión.

## Privacidad de la credencial

1. Iniciar como `qa-asociado-a` y abrir Mi credencial.
2. Sin aceptar guardar, pasar offline: la credencial no debe estar disponible.
3. Volver online, aceptar y comprobar fecha de actualización y vencimiento.
4. Pasar offline y abrirla: debe mostrar sólo los campos mínimos y el aviso de
   validación online.
5. Inspeccionar Cache Storage: no debe existir HTML con nombre o token.
6. Usar “Quitar de este dispositivo” y comprobar que desaparece offline.
7. Guardarla otra vez, cerrar sesión y comprobar que fue eliminada.
8. Iniciar como `qa-asociado-b`: nunca debe verse ningún dato de
   `qa-asociado-a`.
9. Simular una limpieza de logout incompleta y confirmar que la comparación de
   propietario elimina igualmente la copia de A.
10. Adelantar la antigüedad a más de siete días: no debe representarse y debe
    pedir conexión.
11. Limpiar almacenamiento del sitio: la aplicación debe explicar que no hay
    copia, sin romperse.
12. Cambiar el epoch en el servidor. La copia anterior puede seguir visible
    mientras el dispositivo permanezca completamente offline; al recuperar
    conexión y cargar el código nuevo debe eliminarse. La ventana offline
    nunca puede superar los siete días.

## Validación

1. Con el teléfono del asociado offline, mostrar la copia guardada.
2. Con `qa-comercio` online, validar el token contra Uni2.
3. Dar de baja o cambiar el estado en el servidor y repetir: el servidor debe
   decidir el estado vigente.
4. Poner también al comercio offline: la validación debe rechazarse sin quedar
   pendiente.

## Formularios sin conexión

Probar cobro, validación, login, logout y un formulario de gestión:

1. Cortar la red justo antes de enviar.
2. Confirmar el mensaje “no se envió ni quedó pendiente”.
3. Recuperar conexión.
4. Confirmar que la operación no se ejecutó ni se reenvió.
5. Repetir manualmente y comprobar una única operación.

## Actualización

1. Abrir la versión A y comenzar a completar un formulario.
2. Desplegar la versión B en el mismo origen de staging.
3. Confirmar aviso de versión nueva y ausencia de recarga automática.
4. Terminar o descartar el formulario.
5. Aceptar actualizar y confirmar una única recarga.
6. Verificar que cachés de A desaparecieron y que B controla la página.
7. Repetir cerrando todas las ventanas en lugar de aceptar.

## Presentación y accesibilidad

- Tema claro y oscuro.
- Vertical y horizontal.
- Pantalla con notch o isla dinámica y áreas seguras.
- Zoom al 200 %.
- Navegación por teclado y lector de pantalla.
- Avisos de conexión y actualización anunciados sin mover el foco.
- Preferencia de movimiento reducido.

## Evidencia

Registrar navegador, sistema, versión, fecha, URL/build de staging y resultado.
Adjuntar capturas sólo con datos ficticios. Cualquier falla de privacidad,
reenvío de POST o recarga destructiva bloquea el release.

## Ensayo de rollback

1. Desplegar en staging el worker de limpieza en la misma
   `/service-worker.js`.
2. Abrir una instalación existente y esperar su activación.
3. Confirmar eliminación de cachés PWA y almacenamiento privado.
4. Confirmar desregistro del worker y navegación web normal.
5. Mantener el endpoint de limpieza disponible; un 404 no elimina workers ya
   instalados.
