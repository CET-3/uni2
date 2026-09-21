---
type: "Arquitectura"
title: "Backups de producción"
description: "Copias diarias de PostgreSQL e imágenes en un bucket privado R2."
tags: [mvp, arquitectura, producción, backups]
timestamp: 2026-09-20T00:00:00-03:00
---

# Backups de producción

La base PostgreSQL productiva se copia diariamente a `uni2-backup`, un bucket
privado de Cloudflare R2, mediante el workflow `backup-production.yml`. También
puede ejecutarse manualmente con `scripts/backup_production.py`. La copia usa
`pg_dump` 17 en formato custom y contiene solamente el esquema `public` de
Uni2; los esquemas internos de Supabase quedan bajo la operación del proveedor.
Las imágenes viven en `uni2-media` y no forman parte de este dump. Después de
respaldar la base, el mismo workflow copia todos los objetos de `uni2-media` a
`uni2-backup/media/<fecha>/`, conservando sus claves originales. Cada objeto se
descarga del destino y se compara por SHA-256. Una lista vacía, un tamaño
distinto o una copia corrupta hacen fallar el job. Las imágenes se almacenan
sin cifrado adicional, con acceso privado en R2.

El dump se cifra con GPG AES-256 antes de salir del equipo ejecutor. El script
descarga el objeto recién subido, compara SHA-256 y verifica el descifrado
completo. Si falla algún paso, el job termina con error.
No se escribe ningún dump sin cifrar en disco.

`DATABASE_URL`, el endpoint y las credenciales R2, y `BACKUP_PASSPHRASE` son
secretos operativos. La credencial R2 tiene permiso Object Read & Write sólo
sobre `uni2-backup`. La frase de recuperación se guarda además en un gestor de
contraseñas fuera de GitHub y R2. Sin ella no puede restaurarse la copia. El
bucket no tiene dominio público ni acceso `r2.dev`. La retención de 30 días
requiere configurar una regla de ciclo de vida en R2; hasta entonces las
copias no se eliminan automáticamente.

El workflow programado necesita los secrets `BACKUP_DATABASE_URL`,
`BACKUP_R2_ENDPOINT`, `BACKUP_R2_ACCESS_KEY_ID`, `BACKUP_R2_SECRET_ACCESS_KEY` y
`BACKUP_PASSPHRASE`. Se ejecuta sólo desde la rama principal; nunca recibe
secretos un PR. Si falla el job, se crea un Issue con el enlace a la ejecución;
se investiga en GitHub Actions y se repite con `workflow_dispatch` cuando
corresponda. La operación comprueba semanalmente que exista una copia reciente
en R2, incluso si no hubo un job fallido.

La copia de imágenes usa además `MEDIA_R2_ACCESS_KEY_ID` y
`MEDIA_R2_SECRET_ACCESS_KEY`, credenciales Object Read only limitadas a
`uni2-media`. La credencial del backup escribe en `uni2-backup`. Para una
ejecución local, completar estas dos variables en `.env.backup` y ejecutar
`uv run --env-file .env.backup python scripts/backup_media.py`. La regla de
retención de 30 días del bucket de destino debe incluir el prefijo `media/`.
Para probar una restauración, copiar el contenido de un prefijo `media/<fecha>/`
a un bucket nuevo, verificar una muestra de imágenes y apuntar un entorno de
prueba a ese bucket. La base y las imágenes deben elegirse de la misma fecha.

Para recuperar datos se descarga el objeto elegido, se descifra con la frase
guardada y se restaura en una base nueva y aislada, usando `pg_restore` 17.
Primero se comprueba el contenido y la aplicación en esa base. Restaurar sobre
Producción requiere un procedimiento de incidente y autorización explícita.
