---
type: "Arquitectura"
title: "Refresco de datos de staging"
description: "Procedimiento seguro para copiar Producción y endurecer el destino antes de habilitarlo."
tags: [mvp, arquitectura, staging, postgresql, seguridad]
timestamp: 2026-09-03T00:00:00-03:00
---

# Refresco de datos de staging

Un refresco es manual y autorizado. Nunca existe sincronización continua entre
las bases ni se restaura staging hacia Producción.

### Preparación

1. Elegir un identificador único, por ejemplo `2026-08-02-01`.
2. Crear una base PostgreSQL nueva y vacía.
3. Crear dos servicios libpq locales y no versionados:
   `uni2_prod_dump`, con acceso productivo de sólo lectura, y
   `uni2_staging_restore`, con acceso al destino.
4. Confirmar por host, nombre, usuario y huellas de base y rol que origen y
   destino difieren.
5. Mantener el proyecto staging protegido o desconectado durante toda la copia.
6. Configurar `UNI2_PRIVATE_DATA_EPOCH` con el mismo identificador del refresco.

Las URLs, contraseñas y archivos de servicio libpq viven fuera del repositorio.
No se habilita `set -x` ni se colocan secretos en argumentos documentados.

### Copia

La ruta recomendada transmite el dump directamente entre los dos clientes
PostgreSQL y no deja una copia con datos reales en disco:

```bash
pg_dump \
  --dbname="service=uni2_prod_dump" \
  --format=custom \
  --no-owner \
  --no-privileges |
pg_restore \
  --dbname="service=uni2_staging_restore" \
  --single-transaction \
  --exit-on-error \
  --no-owner \
  --no-privileges
```

No se usan `--clean` ni `--create`: el destino debe ser una base nueva. Así,
una equivocación no borra una base existente.

Si el proveedor obliga a generar un archivo, se usa un volumen efímero cifrado
y se lo destruye al terminar. Nunca se guarda en `/tmp` sin verificar cifrado,
ni dentro del repositorio.

#### Copia entre proyectos Supabase

Supabase ya crea y administra esquemas propios en cada proyecto. Uni2 no copia
`auth`, `storage`, `realtime`, `vault` ni otros esquemas del proveedor: copia
únicamente `public`, donde viven las tablas Django. El destino debe tener cero
tablas en `public` antes de comenzar.

Para la operación se usan las URLs **Session pooler** de ambos proyectos,
puerto `5432`. La URL productiva vive temporalmente en
`UNI2_PRODUCTION_COPY_DATABASE_URL`; `DATABASE_URL` apunta al Session pooler de
staging. Ambas quedan en `.env.staging`, ignorado por Git y con permisos `600`.
Las contraseñas no se colocan como argumentos. El runtime serverless de Vercel
usa después la URL **Transaction pooler**, puerto `6543`, y sus huellas se
recalculan para esa URL exacta.

El cliente `pg_dump` debe tener la misma versión mayor que Producción. La copia
validada con PostgreSQL 17 transmite primero el esquema y después los datos,
sin archivos intermedios:

```bash
set -o pipefail
set -a
. ./.env.staging
set +a
export PGOPTIONS='-c default_transaction_read_only=on'

docker run --rm -i \
  -e PGOPTIONS \
  -e UNI2_PRODUCTION_COPY_DATABASE_URL \
  postgres:17 \
  sh -c 'exec pg_dump \
    --dbname="$UNI2_PRODUCTION_COPY_DATABASE_URL" \
    --schema=public \
    --schema-only \
    --no-owner \
    --no-privileges' |
sed '/^CREATE SCHEMA public;$/d' |
docker run --rm -i \
  -e DATABASE_URL \
  postgres:17 \
  sh -c 'exec psql \
    --dbname="$DATABASE_URL" \
    --single-transaction \
    --set=ON_ERROR_STOP=1 \
    --file=-'

docker run --rm -i \
  -e PGOPTIONS \
  -e UNI2_PRODUCTION_COPY_DATABASE_URL \
  postgres:17 \
  sh -c 'exec pg_dump \
    --dbname="$UNI2_PRODUCTION_COPY_DATABASE_URL" \
    --schema=public \
    --data-only \
    --no-owner \
    --no-privileges' |
docker run --rm -i \
  -e DATABASE_URL \
  postgres:17 \
  sh -c 'exec psql \
    --dbname="$DATABASE_URL" \
    --single-transaction \
    --set=ON_ERROR_STOP=1 \
    --command="SET session_replication_role = replica" \
    --file=-'
unset PGOPTIONS
```

La línea eliminada por `sed` es solamente `CREATE SCHEMA public;`: el proyecto
Supabase nuevo ya contiene ese esquema. Cada restauración usa una transacción y
`ON_ERROR_STOP`; ante un error no queda una carga parcial. Después se comparan
los conteos exactos de todas las tablas y los valores de las secuencias.

### Endurecimiento

Con `DATABASE_URL` apuntando al destino y los settings de staging completos,
primero se revisa y aplica el esquema compatible:

```bash
DJANGO_SETTINGS_MODULE=config.settings.staging \
uv run python manage.py migrate --plan

DJANGO_SETTINGS_MODULE=config.settings.staging \
uv run python manage.py migrate
```

Después se ejecuta el endurecimiento:

```bash
DJANGO_SETTINGS_MODULE=config.settings.staging \
uv run python manage.py preparar_copia_staging \
  --refresh-id 2026-08-02-01 \
  --confirm-target uni2-staging
```

Las contraseñas QA llegan mediante variables temporales:

- `UNI2_STAGING_QA_ADMIN_USERNAME`
- `UNI2_STAGING_QA_ADMIN_PASSWORD`
- `UNI2_STAGING_QA_ASOCIADO_A_USERNAME`
- `UNI2_STAGING_QA_ASOCIADO_A_PASSWORD`
- `UNI2_STAGING_QA_ASOCIADO_B_USERNAME`
- `UNI2_STAGING_QA_ASOCIADO_B_PASSWORD`
- `UNI2_STAGING_QA_COMERCIO_USERNAME`
- `UNI2_STAGING_QA_COMERCIO_PASSWORD`

No se pasan contraseñas como argumentos. El comando ejecuta todos los cambios
en una transacción y revierte ante cualquier error. Como último cambio de esa
misma transacción escribe `EstadoDatosStaging`; hasta entonces, el middleware y
readiness responden `503`.

### Rotación de contraseñas QA

Cuando la copia ya está endurecida y las cuatro cuentas QA existen, no se debe
volver a ejecutar `preparar_copia_staging`: ese comando crea cuentas nuevas y
rechaza usernames que ya existen. Para cambiar solamente sus contraseñas se
usa:

```bash
DJANGO_SETTINGS_MODULE=config.settings.staging \
uv run python manage.py rotar_passwords_qa_staging
```

El comando toma los mismos ocho valores `UNI2_STAGING_QA_*` del entorno,
verifica que cada username corresponda al perfil QA esperado y actualiza sólo
las contraseñas dentro de una transacción. Las contraseñas deben ser distintas,
tener al menos 8 caracteres y no coincidir con sus usernames. Si una
validación falla, no se modifica ninguna cuenta.

Luego se verifica:

- cero sesiones copiadas;
- ningún usuario productivo activo;
- contraseñas productivas inutilizables;
- cero privilegios productivos `staff` o `superuser`;
- tokens de credencial regenerados y únicos;
- sólo cuatro cuentas QA habilitadas;
- dos asociados y un comercio QA contienen datos ficticios inequívocos;
- marcador `EstadoDatosStaging` igual al refresh ID;
- conteos agregados razonables;
- manifest `UNI2 STG`;
- barrera HTTP y `noindex`;
- correo transaccional en `disabled` durante el refresco; una activación
  posterior sólo puede usar `redirect` hacia la casilla segura;
- correo por lote y push deshabilitados.

### Copia de archivos media

La copia PostgreSQL conserva las rutas de `Comercio.foto` y
`Publicidad.foto`, pero no descarga los objetos del storage productivo. Para
que la réplica sea visualmente representativa se usa un bucket privado,
exclusivo de staging y con credenciales de escritura limitadas a ese bucket.
No se conecta staging al bucket productivo.

El storage se configura localmente y en el proyecto Vercel de staging con:

- `UNI2_STAGING_AWS_STORAGE_BUCKET_NAME`;
- `UNI2_STAGING_AWS_ACCESS_KEY_ID`;
- `UNI2_STAGING_AWS_SECRET_ACCESS_KEY`;
- `UNI2_STAGING_AWS_S3_ENDPOINT_URL`;
- `UNI2_STAGING_AWS_S3_REGION_NAME`;
- `UNI2_STAGING_STORAGE_FINGERPRINT`;
- `UNI2_PRODUCTION_STORAGE_FINGERPRINT`.

Las huellas identifican bucket, endpoint y dominio personalizado, pero no
incluyen claves. Se calculan con:

```bash
uv run python manage.py huella_storage \
  --bucket NOMBRE \
  --endpoint URL_S3 \
  --custom-domain DOMINIO_PUBLICO_OPCIONAL
```

Primero se revisa cuántas referencias vigentes copiará el comando:

```bash
DJANGO_SETTINGS_MODULE=config.settings.staging \
uv run python manage.py copiar_media_staging \
  --source-base-url https://DOMINIO_PUBLICO_PRODUCTIVO \
  --confirm-target uni2-staging
```

Después se repite agregando `--confirmar`. El comando sólo considera rutas
vigentes bajo `comercios/` y `publicidades/`, exige HTTPS e imágenes menores a
10 MB, conserva el nombre registrado en la base y omite objetos que ya existen
en staging. Si una descarga falla, informa una copia parcial y puede repetirse
sin duplicar los objetos aprobados.

Las credenciales productivas no participan: el origen son las mismas URLs
públicas que ya entrega el sitio. El destino genera URLs firmadas breves,
permanece sin dominio público y nunca usa las variables `AWS_*` productivas.

Cambiar una variable de Vercel no modifica deployments existentes. El cutover
de la base y `UNI2_PRIVATE_DATA_EPOCH` siempre se completa con un deployment
nuevo; no se promueve una versión que todavía renderice el epoch anterior.

Las huellas no reversibles de la base y del rol se obtienen con:

```bash
uv run python manage.py huella_base
uv run python manage.py huella_base --rol
```

La huella de base considera usuario, host, puerto y nombre. El usuario es
necesario porque los poolers compartidos de Supabase pueden usar el mismo host,
puerto y nombre `postgres` para proyectos distintos, y codifican la referencia
del proyecto en el usuario de conexión. Ninguna huella incluye la contraseña.

### Cierre

Después de habilitar la base nueva:

1. copiar y verificar los media referenciados cuando el bucket staging esté
   habilitado;
2. ejecutar smoke tests y la matriz PWA;
3. mantener el destino anterior desconectado durante la ventana de rollback;
4. destruir cualquier artefacto temporal cifrado, si el proveedor obligó a
   crearlo;
5. revocar la credencial productiva de sólo lectura;
6. retirar `UNI2_PRODUCTION_COPY_DATABASE_URL` y las contraseñas temporales de
   creación de usuarios QA;
7. registrar fecha, responsable, refresh ID, conteos y resultado, nunca datos.

Una exposición de staging se trata como un incidente sobre datos productivos.
