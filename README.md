# Uni2

## Correr localmente

### 1. Crear entorno virtual

```bash
cd /home/milena/CET3/uni2
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
```

### 2. Configurar base de datos

Por defecto el proyecto usa SQLite.

Si queres usar PostgreSQL, exporta estas variables:

```bash
cp .env.example .env
```

Luego ajusta `.env` si necesitas cambiar el nombre de la base o el usuario.

En esta maquina PostgreSQL esta funcionando por socket local, asi que no hace falta
usar `127.0.0.1` ni password si te conectas como `root`.

Antes de migrar, crea la base:

```bash
createdb uni2
```

Django carga `.env` automaticamente al iniciar.

### 3. Crear migraciones y aplicar esquema

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### 4. Cargar datos iniciales

```bash
python3 manage.py bootstrap_uni2
```

Esto crea:

- grupos base
- colegio CET 3
- cursos iniciales
- cuentas contables iniciales
- usuario administrador local

Usuario inicial:

- username: `admin`
- password: `admin1234`

### 5. Levantar servidor

```bash
python3 manage.py runserver
```

Admin Django:

- http://127.0.0.1:8000/admin/
