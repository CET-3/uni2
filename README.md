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

Variables de entorno necesarias en Vercel:
- `SECRET_KEY`
- `DATABASE_URL`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`

La base de datos de producción es Supabase (PostgreSQL). Para correr migraciones en producción:

```bash
DATABASE_URL=<url-de-supabase> uv run python manage.py migrate
```
