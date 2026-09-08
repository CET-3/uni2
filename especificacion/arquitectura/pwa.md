---
type: "Arquitectura"
title: "Progressive Web App"
description: "Manifest, service worker, almacenamiento y límites de la PWA de Uni2."
tags: [pwa, arquitectura, seguridad, offline]
timestamp: 2026-08-01T00:00:00-03:00
---

# Progressive Web App

Uni2 sigue siendo una aplicación Django con templates y mejora
progresivamente cuando el navegador admite PWA. El servidor conserva la
autoridad sobre autenticación, permisos, pagos y validación de credenciales.
Un navegador sin service workers debe poder usar el sitio normalmente.

## Componentes

- El web app manifest define identidad, inicio, alcance, presentación e
  iconos.
- El service worker vive en la raíz para controlar todo el alcance `/`.
- Un script cliente registra el worker y coordina instalación, conexión,
  actualización y almacenamiento privado.
- Mientras se navega desde el browser y la aplicación no está instalada, una
  invitación visible ofrece instalarla. Usa el diálogo nativo cuando el
  navegador lo permite y, en los demás casos, explica la opción manual del
  menú sin abrirla automáticamente.
- La pantalla general offline no consulta la base ni contiene información de
  una sesión.
- La credencial offline usa IndexedDB en la base `uni2-private-v1`, store
  `credentials`, registro `active`. No se guarda una copia de la página
  autenticada.

La PWA no necesita modelos ni migraciones. La copia de credencial pertenece al
dispositivo, no a la base del servidor.

## Identidad estable

El manifest usa:

- `id`: `/`
- `name`: `UNI2 - Mutual Escolar`
- `short_name`: `UNI2`
- `lang`: `es-AR`
- `start_url`: `/`
- `scope`: `/`
- `display`: `standalone`
- `theme_color`: `#3f51b5`
- `background_color`: `#f7f9fc`

Los iconos incluyen variantes normales y `maskable` de 192 y 512 píxeles,
además del icono Apple de 180 píxeles. La identidad y el origen productivo
deben mantenerse estables antes de agregar notificaciones push en otra etapa.

## Contexto seguro

Los service workers funcionan en HTTPS y, como excepción de desarrollo, en
`localhost` o direcciones loopback. Una dirección de red local como
`http://192.168.x.x:8000` no sirve para probar la PWA en un teléfono.

Las pruebas físicas se realizan en un staging HTTPS separado, con base,
storage, secreto y accesos propios. La base puede ser una copia puntual de
Producción únicamente después del
[endurecimiento de staging](refresco-staging.md): no conserva sesiones, pero
conserva contraseñas, privilegios y tokens productivos por decisión explícita.
La barrera HTTP y el aislamiento de base deben estar activos antes de probar
las credenciales copiadas. Los previews nunca reciben recursos remotos.

## Política de respuestas

El servidor distingue explícitamente las respuestas públicas anónimas que el
worker puede reutilizar. Una URL por sí sola no alcanza, porque una página
pública puede incluir navegación personalizada cuando existe una sesión.

- HTML autenticado: `Cache-Control: private, no-store`.
- Login, logout, admin, gestión y formularios: `private, no-store`.
- HTML público anónimo permitido: `X-Uni2-PWA-Cacheable: public` y
  `Vary: Cookie`.
- Manifest y worker: revalidación contra el servidor.
- El worker sólo persiste respuestas exitosas, del mismo origen y marcadas
  como públicas.

La Cache API no decide por sí sola si una respuesta privada puede guardarse.
El worker verifica los encabezados antes de escribir.

## Estrategias

| Recurso | Estrategia | Sin conexión |
|---|---|---|
| CSS, JavaScript, fuentes, logos e iconos versionados | cache-first | Disponible |
| Archivos estáticos en desarrollo local | network-first con `cache: no-store` | Última copia obtenida |
| Pantalla offline y shell mínimo | precache | Disponible |
| Página pública anónima permitida | network-first | Última versión visitada |
| Imagen pública permitida | stale-while-revalidate con límite | Disponible si fue vista |
| `/` | network-first sin persistir HTML personalizado | Pantalla offline |
| Página autenticada | network-only | Pantalla o aviso offline |
| Credencial guardada | IndexedDB, no Cache Storage | Disponible hasta siete días |
| POST, upload, pago o validación | network-only | Falla informada, sin reintento |

Los cachés llevan `PWA_BUILD_ID`, derivado del commit de Vercel en producción,
y el epoch privado de la copia de datos. Al activarse una versión se eliminan
solamente cachés PWA de builds o epochs anteriores.

En desarrollo local los archivos mantienen una URL estable y el build se llama
`development`. Para que esa combinación no deje CSS o JavaScript viejos, el
worker consulta siempre la red y actualiza su copia de respaldo. Una nueva
versión del worker se activa inmediatamente en desarrollo. Staging y producción
conservan archivos versionados, `cache-first` y actualización confirmada por la
persona usuaria.

## Actualización

El worker se registra desde `/static/pwa/uni2-pwa.js` con scope `/` y
`updateViaCache: "none"`. Una versión nueva permanece en espera. La interfaz
avisa y, al aceptar, envía el mensaje `SKIP_WAITING`. No se recarga una
pantalla automáticamente mientras se completa un formulario. Después de
`controllerchange` se permite una sola recarga.

La espera y confirmación corresponden a staging y producción. En desarrollo el
worker usa `skipWaiting` automáticamente para evitar que una implementación
anterior continúe controlando los archivos estáticos locales.

## Privacidad de la credencial

La página autenticada y su HTML nunca entran en Cache Storage. Sólo después de
aceptar “Guardar en este dispositivo” se crea un registro mínimo en IndexedDB.

El registro contiene:

- versión de esquema;
- propietario como SHA-256 del origen y el ID de usuario, nunca el ID crudo;
- nombre, apellido, número, tipo y estado al guardar;
- token de credencial;
- URL absoluta de resolución de la credencial;
- fechas de actualización y vencimiento.

Un registro con más de siete días no se muestra y se elimina. Al cerrar sesión
se limpia el registro. Al iniciar con otra cuenta, la identidad recibida del
servidor se compara antes de mostrar datos y cualquier registro ajeno se
elimina. La interfaz también ofrece “Quitar de este dispositivo”.

Un cambio de epoch sólo puede llegar a un dispositivo cuando vuelve a
conectarse. Mientras permanezca completamente offline puede conservar la copia
anterior hasta que venza el límite local de siete días; no se promete una
revocación remota durante el offline absoluto.

El QR se genera localmente desde la URL entregada por el servidor. Una copia
anterior sin ese campo reconstruye la ruta desde su origen y token hasta que
una visita online la actualiza. El almacenamiento local no
convierte la credencial en vigente: la decisión de validez sigue perteneciendo
al servidor cuando el comercio consulta el token.

## Operaciones que no se encolan

El worker no usa Background Sync. Un POST sin red:

1. hace un único intento;
2. no se escribe en Cache Storage ni IndexedDB;
3. no se reenvía al recuperar conexión;
4. informa: “La operación no se envió ni quedó pendiente. Revisá la conexión
   y volvé a intentarlo”.

Esta regla evita cobros, validaciones y cambios duplicados.

## Preparación para etapas futuras

La URL del worker y sus responsabilidades quedan claras para poder agregar
eventos push más adelante. En esta etapa no se implementan handlers `push`,
permisos, suscripciones ni correo. El envío de mails será infraestructura de
backend independiente del ciclo de vida PWA.
