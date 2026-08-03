---
type: "Pruebas manuales"
title: "Staging y refresco de datos"
description: "Controles operativos antes de habilitar una copia y antes de promover a Producción."
tags: [mvp, staging, pruebas, seguridad]
timestamp: 2026-08-02T00:00:00-03:00
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
- [ ] Todos los usuarios productivos están inactivos.
- [ ] Sus contraseñas son inutilizables.
- [ ] Ninguno conserva `staff` o `superuser`.
- [ ] Todos los tokens de credencial cambiaron.
- [ ] Sólo cuatro cuentas QA están activas: admin, dos asociados ficticios y
  comercio ficticio.
- [ ] Ninguna cuenta QA está vinculada a una persona o comercio productivo.
- [ ] El marcador persistente coincide con `UNI2_PRIVATE_DATA_EPOCH`.
- [ ] El bucket productivo no está configurado en staging.
- [ ] Correo transaccional, correo por lote y push están deshabilitados.

### PWA

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
