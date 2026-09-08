---
type: "Pruebas manuales"
title: "Staging y refresco de datos"
description: "Controles operativos antes de habilitar una copia y antes de promover a Producción."
tags: [mvp, staging, pruebas, seguridad]
timestamp: 2026-09-03T00:00:00-03:00
---

# Staging y refresco de datos

### Seguridad de acceso

- [ ] La URL sin autorización responde `401`.
- [ ] La respuesta incluye `X-Robots-Tag: noindex, nofollow, noarchive`.
- [ ] Las credenciales HTTP de staging no funcionan en Producción.
- [ ] Después de la barrera HTTP, Uni2 continúa exigiendo su propio login.
- [ ] La pantalla, el título y la aplicación instalada muestran `STAGING`.

### Copia de datos

- [ ] La base staging tiene host, nombre, usuario, huellas de base/rol y
  secreto distintos.
- [ ] Readiness responde `503` antes de terminar el endurecimiento.
- [ ] No existe ninguna sesión copiada.
- [ ] La cantidad de usuarios, asociados y comercios coincide con Producción.
- [ ] Los hashes de contraseña, estado, grupos, permisos, `staff` y
  `superuser` coinciden con Producción.
- [ ] Las relaciones de usuarios con asociados y comercios coinciden con
  Producción.
- [ ] Los tokens de credencial coinciden con Producción.
- [ ] Se confirma en una prueba controlada que una cuenta copiada conserva su
  autenticación en staging.
- [ ] El acceso HTTP, el aislamiento de base y el `noindex` están activos
  antes de probar las credenciales copiadas.
- [ ] El marcador persistente coincide con `UNI2_PRIVATE_DATA_EPOCH`.
- [ ] El bucket productivo no está configurado en staging.
- [ ] El bucket staging es privado, exclusivo y usa credenciales limitadas a
  ese destino.
- [ ] Todas las rutas `Comercio.foto` y `Publicidad.foto` vigentes existen en
  el bucket staging y se muestran mediante URLs firmadas.
- [ ] Durante el refresco, correo transaccional, correo por lote y push están
  deshabilitados.
- [ ] Si se prueba SMTP, el correo transaccional usa `redirect`, entrega sólo a
  la casilla segura y marca el asunto con `[STAGING]`; `enabled` está rechazado.
- [ ] Correo por lote y push permanecen deshabilitados durante toda la prueba.

### PWA

- [ ] Manifest, worker, shell offline y archivos estáticos cargan sin depender
  de la cabecera HTTP Basic; ninguna vista de negocio queda exceptuada.
- [ ] El service worker queda activo y controla la aplicación.
- [ ] La invitación de instalación es visible al navegar y desaparece en modo
  instalado.
- [ ] El manifest usa `UNI2 STG` y los iconos llevan la insignia `STG`.
- [ ] Staging y Producción pueden instalarse como aplicaciones separadas.
- [ ] El banner también aparece en las pantallas offline.
- [ ] Un cambio de `UNI2_PRIVATE_DATA_EPOCH` elimina la credencial offline previa.
- [ ] Se confirma que esa eliminación ocurre al reconectar; no se promete
  revocación remota durante el offline absoluto.
- [ ] Se prueba una versión A y una B sobre el mismo dominio staging.

### Promoción

- [ ] `pytest (SQLite)` y `Endurecimiento staging (PostgreSQL)` están aprobados.
- [ ] Las migraciones staging fueron aplicadas y verificadas.
- [ ] El workflow probó acceso anónimo, readiness, manifest, iconos, worker y
  pantalla offline antes de promover el deployment.
- [ ] El dominio estable informa el mismo SHA después de la promoción.
- [ ] El PR `staging -> main` contiene solamente la versión aceptada.
