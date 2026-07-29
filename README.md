# Uni2

Sistema de gestión para la Mutual Escolar del CET 3.

## Requisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

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

Para probar desde un teléfono conectado a la misma red Wi-Fi que la computadora:

```bash
uv run python manage.py runserver 0.0.0.0:8000
```

Después abrir desde el teléfono:

```text
http://192.168.18.138:8000
```

Usuarios ficticios creados sólo en desarrollo local:

- Gestión/admin técnico: `admin` / `admin1234`
- Atención de mutual y asociado de prueba: `atencion` / `atencion1234`
- Asociado de prueba: `asociado` / `asociado1234`
- Comercio de prueba: `comercio` / `comercio1234`

La app corre en http://127.0.0.1:8000

También queda habilitada para desarrollo local desde `http://192.168.18.138:8000`.

## Tests

```bash
# Usa el motor configurado en el archivo .env
uv run pytest

# Verificación explícita con SQLite
DB_ENGINE=sqlite uv run pytest
```

Cada PR y cada actualización de `main` ejecutan la misma suite con SQLite en
GitHub Actions. El check requerido se llama `pytest (SQLite)`.

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

Vercel acepta deploys automáticos únicamente desde `main`. Los previews de
otros branches están deshabilitados hasta disponer de una base PostgreSQL
separada de producción.

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
