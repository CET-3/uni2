# Uni2

Sistema de gestión para la Mutual Escolar del CET 3.

## Requisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

Si es tu primera vez con Python, Windows o Django, seguí la
[Guía para empezar con Python, uv y Django en Windows](especificacion/guia-windows-python-django.md).

## Setup local para alumnos (SQLite)

SQLite viene incluido con Python y no requiere instalar ni configurar un
servidor de base de datos.

```bash
# Instalar dependencias
uv sync

# Usar el perfil local con SQLite
cp .env.example .env

# Aplicar migraciones
uv run python manage.py migrate

# Cargar datos iniciales
uv run python manage.py carga_inicial

# Levantar servidor
uv run python manage.py runserver
```

La base se guarda en el archivo local `db.sqlite3`. Ese archivo no se versiona
y cada alumno tiene sus propios datos.

## Setup local con PostgreSQL

Quienes tengan PostgreSQL instalado pueden usar el mismo proyecto y los mismos
settings con otro archivo de variables:

```bash
uv sync
cp .env.postgres.example .env
```

Después hay que editar `.env` con las credenciales locales, crear la base
indicada en `DB_NAME` y ejecutar los mismos comandos:

```bash
uv run python manage.py migrate
uv run python manage.py carga_inicial
uv run python manage.py runserver
```

En ambos perfiles Django usa `config.settings.local`. `DB_ENGINE` selecciona
`sqlite` o `postgres`; no hace falta modificar código para cambiar de motor.

Para revisar el sitio web desde un teléfono conectado a la misma red Wi-Fi:

```bash
uv run python manage.py runserver 0.0.0.0:8000
```

Después abrir desde el teléfono:

```text
http://192.168.18.138:8000
```

Esa dirección HTTP sirve para revisar páginas responsive, pero **no sirve para
probar la PWA**: un service worker necesita HTTPS o, durante desarrollo,
`localhost`/loopback. La PWA se prueba localmente desde
<http://127.0.0.1:8000/> en la misma computadora. Para Android o iOS reales se
usa un staging HTTPS separado. Su base puede partir de una copia productiva
endurecida, pero nunca comparte conexión, sesiones, contraseñas, tokens,
`SECRET_KEY` ni storage con Production.

Usuarios ficticios creados sólo en desarrollo local:

- Gestión/admin técnico: `admin` / `admin1234`
- Atención al asociado y asociado de prueba: `atencion` / `atencion1234`
- Asociado de prueba: `asociado` / `asociado1234`
- Comercio de prueba: `comercio` / `comercio1234`

La app corre en <http://127.0.0.1:8000/>.

También queda habilitada para desarrollo local desde `http://192.168.18.138:8000`.

## PWA

Uni2 puede instalarse como una única aplicación desde `/`. Con conectividad
limitada conserva el shell y contenido público seguro. Las páginas
autenticadas no se guardan en el caché general.

El asociado puede elegir guardar su credencial en ese dispositivo durante
siete días. La copia se elimina al cerrar sesión, cambiar de usuario, vencer o
usar “Quitar de este dispositivo”. El comercio siempre necesita conexión para
validarla. Si cambia el epoch de datos, la copia anterior se elimina cuando el
dispositivo vuelve a conectarse; el offline absoluto no permite revocación
remota antes del vencimiento local.

Esta etapa no incluye notificaciones push ni correos transaccionales o por
lote.

## Tests

```bash
# Usa el motor configurado en el archivo .env
uv run pytest

# Verificación explícita con SQLite
DB_ENGINE=sqlite uv run pytest

# Contratos Django de la PWA
DB_ENGINE=sqlite uv run pytest pwa/tests config/tests/test_pwa_config.py -q

# Confirmar que no aparecieron migraciones
DB_ENGINE=sqlite uv run python manage.py makemigrations --check --dry-run

# Generar y revisar estáticos como en producción
DJANGO_SETTINGS_MODULE=config.settings.production \
SECRET_KEY=collectstatic-local \
DATABASE_URL=sqlite:///:memory: \
uv run python manage.py collectstatic --noinput
```

Cada PR y cada actualización de `main` ejecutan la suite con SQLite y los
controles de endurecimiento sobre un PostgreSQL efímero. Un push a `staging`
reutiliza esos mismos checks antes de desplegar. Los jobs se llaman
`pytest (SQLite)` y `Endurecimiento staging (PostgreSQL)`.

## Colaboración

Todos los cambios se entregan mediante PRs. El paso a paso para crear una rama,
probar y abrir el PR está en [CONTRIBUTING.md](CONTRIBUTING.md).

## Agregar dependencias

```bash
# Dependencia de producción
uv add nombre-paquete

# Dependencia de desarrollo (tests, herramientas)
uv add --dev nombre-paquete

# Siempre commitear pyproject.toml y uv.lock juntos
git add pyproject.toml uv.lock
```

## Deploy

La versión pública de Production está en
<https://uni2-ashy.vercel.app/>.

Vercel acepta deploys Git automáticos únicamente desde `main`. Los previews de
los PR permanecen deshabilitados.

La rama permanente `staging` se despliega mediante GitHub Actions sobre el
proyecto Vercel separado `uni2-staging`. El workflow espera ambos jobs de CI,
despliega sin mover el dominio estable, prueba autorización, readiness,
manifest, iconos, worker y pantalla offline, y recién entonces promueve la
versión. Después comprueba el SHA sobre el dominio estable.

Cuando la integración Git está habilitada, fusionar un PR en `main` inicia el
deploy productivo. Como alternativa manual y controlada:

```bash
vercel deploy --prod --skip-domain
vercel inspect URL_DEL_DEPLOY --wait
vercel promote URL_DEL_DEPLOY
```

Vercel detecta `manage.py`, instala el entorno desde `pyproject.toml` y
`uv.lock`, encuentra la aplicación WSGI y publica los archivos estáticos en su
CDN. `vercel.json` declara el preset `django` para que esta detección tenga
prioridad incluso si el proyecto remoto conservaba el preset `Other` de una
configuración anterior. `staticfiles/` es un artefacto del deploy: no se
prepara ni se versiona manualmente.

Variables de entorno de **Production** necesarias en Vercel:

- `SECRET_KEY`
- `DATABASE_URL`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`

`ALLOWED_HOSTS` lleva nombres de dominio sin `https://`;
`CSRF_TRUSTED_ORIGINS`, orígenes completos con `https://`. Los hosts exactos
generados por Vercel se agregan automáticamente mediante sus variables de
sistema. En Vercel debe permanecer habilitada la opción **Automatically expose
System Environment Variables**.

`DEBUG` está deshabilitado por código en producción y no se configura mediante
una variable. `SECRET_KEY` debe ser un valor aleatorio largo; cambiarlo cierra
las sesiones existentes.

### Staging

El proyecto `uni2-staging` usa `config.settings.staging`, una base PostgreSQL y
un `SECRET_KEY` propios. También exige:

- `UNI2_ENVIRONMENT=staging`
- `UNI2_STAGING_ACCESS_USERNAME`
- `UNI2_STAGING_ACCESS_PASSWORD`
- `UNI2_STAGING_DATABASE_LABEL`
- `UNI2_STAGING_DATABASE_FINGERPRINT`
- `UNI2_PRODUCTION_DATABASE_FINGERPRINT`
- `UNI2_STAGING_DATABASE_ROLE_FINGERPRINT`
- `UNI2_PRODUCTION_DATABASE_ROLE_FINGERPRINT`
- `UNI2_PRIVATE_DATA_EPOCH`

El proyecto usa Vercel Authentication y el perfil agrega una segunda barrera
HTTP, `noindex`, respuestas `private, no-store`, un banner visible, iconos con
insignia `STG`, un nombre PWA distinto y bloquea correo transaccional, correo
por lote y push. Si no existe un marcador de copia endurecida para el epoch
actual, responde `503`.

Los archivos media quedan deshabilitados por defecto. Un bucket staging
opcional debe ser privado, exclusivo y configurarse solamente mediante
variables `UNI2_STAGING_AWS_*`; nunca se heredan variables AWS productivas. El
comando `copiar_media_staging` replica únicamente las imágenes vigentes desde
su origen público y no necesita credenciales del bucket productivo.

La base puede clonarse desde Producción sólo mediante el
[procedimiento de refresco](especificacion/arquitectura/refresco-staging.md).
Antes de conectarla es obligatorio ejecutar:

```bash
DJANGO_SETTINGS_MODULE=config.settings.staging \
uv run python manage.py preparar_copia_staging \
  --refresh-id ID_DEL_REFRESCO \
  --confirm-target uni2-staging
```

Antes del comando se aplican las migraciones compatibles a la base staging
todavía desconectada. El comando elimina sesiones, invalida usuarios
productivos, retira privilegios, regenera tokens de credencial y crea cuatro
accesos exclusivos: un admin, dos asociados ficticios y un comercio ficticio.
Esos perfiles permiten recorrer la matriz PWA sin vincular cuentas QA a
personas reales. El marcador de readiness se escribe como último paso
transaccional. Las contraseñas QA llegan por variables temporales y nunca por
argumentos o archivos versionados.

La configuración completa y el circuito de promoción están en
[Entorno de staging](especificacion/arquitectura/staging.md).
El inventario de variables y secretos está en
[Configuración de deploy](especificacion/arquitectura/deploy.md).

### Migraciones en producción

El arranque de la aplicación en Vercel no ejecuta migraciones ni comandos de
carga. Cuando un PR incluye migraciones, después de aprobarlo y antes de
fusionarlo se revisa el plan usando las variables de Production guardadas en
Vercel:

```bash
vercel env run --environment production -- \
  env DJANGO_SETTINGS_MODULE=config.settings.production \
  uv run python manage.py migrate --plan
```

Si el plan es correcto y existe un respaldo adecuado para un cambio riesgoso:

```bash
vercel env run --environment production -- \
  env DJANGO_SETTINGS_MODULE=config.settings.production \
  uv run python manage.py migrate
```

Las migraciones deben ser compatibles con la versión que continúa atendiendo
tráfico hasta que se fusione el PR. Los cambios destructivos se dividen en más
de una entrega.

`carga_inicial` contiene usuarios y contenido ficticios. Sólo funciona con
settings locales o de test y nunca se ejecuta sobre producción.

### Verificación de la PWA desplegada

Sobre la URL HTTPS de staging o Production:

```bash
curl --fail --silent --show-error --output /dev/null --dump-header - \
  https://DOMINIO/manifest.webmanifest
curl --fail --silent --show-error --output /dev/null --dump-header - \
  https://DOMINIO/service-worker.js
curl --fail --silent --show-error --output /dev/null --dump-header - \
  https://DOMINIO/sin-conexion/
```

El manifest debe usar `application/manifest+json`. El worker debe usar un tipo
JavaScript, `Service-Worker-Allowed: /` y `Cache-Control` de revalidación. En
DevTools se verifica además que el scope sea `/`, que los iconos existan y que
Cache Storage no contenga HTML autenticado.

Antes de promover se completa la matriz de
[pruebas manuales PWA](especificacion/pruebas-manuales/pwa.md), incluida la
privacidad al cambiar de usuario, POST offline, actualización con formulario y
rollback.

### Rollback de PWA

No se elimina simplemente `/service-worker.js`: los dispositivos instalados
conservarían la versión anterior. Para retirar la PWA se despliega en esa misma
URL un worker de limpieza que borra cachés Uni2 y la credencial privada, se
desregistra y deja el sitio funcionando como web normal. El procedimiento se
ensaya primero en staging y se mantiene el endpoint el tiempo suficiente para
alcanzar dispositivos que vuelvan a conectarse.
