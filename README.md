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

Usuarios iniciales:

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

El deploy es automático via GitHub → Vercel al hacer push a `main`.

Para deployar manualmente:

```bash
vercel --prod
```

Variables de entorno necesarias en Vercel (setear desde el dashboard):
- `SECRET_KEY`
- `DATABASE_URL`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`

### Migraciones y carga inicial en producción

Las migraciones **no** se ejecutan automáticamente dentro de la función serverless
de Vercel (se eliminó para no saturar el pool de conexiones de Supabase).
Tampoco los comandos de gestión (`carga_inicial`).

Para correrlos hay que hacerlo desde la máquina local apuntando a la base de
producción. Obtené la DATABASE_URL desde el dashboard de Vercel
(Project → Settings → Environment Variables) o desde Supabase
(Supabase → Project Settings → Database → Connection string → URI):

```bash
# Migraciones
DATABASE_URL="postgresql://..." uv run python manage.py migrate

# Carga inicial de datos (idempotente)
DATABASE_URL="postgresql://..." uv run python manage.py carga_inicial
```

> **Importante**: después de correr migraciones o carga inicial, si el deploy
> anterior falló, hacer un nuevo push (commit vacío o reploy manual desde Vercel)
> para que la función serverless arranque fresca con la base actualizada.
