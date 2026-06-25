# Uni2

Sistema de gestión para la Mutual Escolar del CET 3.

## Requisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Setup local

```bash
# Instalar dependencias
uv sync

# Copiar variables de entorno
cp .env.example .env
# Editar .env con las credenciales locales si es necesario

# Aplicar migraciones
uv run python manage.py migrate

# Cargar datos iniciales
uv run python manage.py carga_inicial

# Levantar servidor
uv run python manage.py runserver
```

Usuarios iniciales:

- Gestión/admin técnico: `admin` / `admin1234`
- Atención de mutual y asociado de prueba: `atencion` / `atencion1234`
- Asociado de prueba: `asociado` / `asociado1234`
- Comercio de prueba: `comercio` / `comercio1234`

La app corre en http://127.0.0.1:8000

## Tests

```bash
uv run pytest
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
