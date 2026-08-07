# Guía para empezar con Python, uv y Django en Windows

Esta guía está pensada para quienes recién empiezan a programar y van a
trabajar en Uni2. Los comandos se ejecutan desde **PowerShell**.

También hay más apuntes y material de apoyo en
[apuntes-eight.vercel.app](https://apuntes-eight.vercel.app/).

## Antes de empezar: ¿qué es PowerShell?

PowerShell es una aplicación de Windows donde podemos escribir comandos para
trabajar con carpetas, archivos y programas. Es parecida al “Símbolo del
sistema” o `cmd`, pero tiene comandos más modernos y es la herramienta que
usaremos en esta guía.

Para abrirlo:

1. Presionar la tecla Windows.
2. Escribir **PowerShell**.
3. Abrir **Windows PowerShell** o **PowerShell**.

Se abrirá una ventana azul, negra o blanca con una línea parecida a esta:

```text
PS C:\Users\TuNombre>
```

El texto que aparece antes del símbolo `>` indica en qué carpeta estamos. Los
comandos de esta guía se escriben después de ese símbolo y se ejecutan con
**Enter**.

Para cerrar PowerShell se puede escribir `exit` y presionar Enter, o cerrar la
ventana normalmente.

### Usar la terminal desde Visual Studio

También se pueden ejecutar estos mismos comandos desde la terminal integrada
de **Visual Studio Code** o **Visual Studio**. En Visual Studio Code se abre
desde **Terminal → New Terminal**. En Visual Studio se abre desde
**View → Terminal**.

La terminal integrada funciona igual que la ventana de PowerShell: los
comandos se escriben después del símbolo `>` y se ejecutan con Enter. Conviene
verificar que la terminal seleccionada diga **PowerShell**.

## 1. Instalar Python

1. Entrar a la página oficial de [Python 3.12.10 para Windows](https://www.python.org/downloads/release/python-31210/).
2. Descargar **Windows installer (64-bit)**.
3. Abrir el instalador y marcar **Add python.exe to PATH**.
4. Elegir **Install Now**.
5. Cerrar y volver a abrir PowerShell.

Comprobar la instalación:

```powershell
py --version
python --version
```

Tiene que aparecer una versión 3.12 o superior. Si `python` abre Microsoft
Store, usar `py` o desactivar los alias `python.exe` y `python3.exe` desde
**Administrar alias de ejecución de aplicaciones** en Windows.

## 2. Instalar uv

`uv` administra versiones de Python, entornos virtuales y dependencias.

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Cerrar y volver a abrir PowerShell. Comprobar:

```powershell
uv --version
```

También se puede instalar con `winget`:

```powershell
winget install --id=astral-sh.uv -e
```

Documentación oficial: [Instalación de uv](https://docs.astral.sh/uv/getting-started/installation/).

## 3. Python básico

Python es el lenguaje y sus archivos terminan en `.py`.

```powershell
mkdir practica-python
cd practica-python
notepad hola.py
```

Pegar, guardar y ejecutar:

```python
nombre = input("¿Cómo te llamás? ")
edad = int(input("¿Qué edad tenés? "))

print(f"Hola, {nombre}.")
print(f"El año que viene vas a tener {edad + 1} años.")
```

```powershell
python hola.py
```

Ejemplos de tipos, condiciones, listas y funciones:

```python
nombre = "Ana"       # str: texto
edad = 16             # int: entero
activo = True         # bool: verdadero o falso

if edad >= 18:
    print("Es mayor de edad")
else:
    print("Es menor de edad")

frutas = ["manzana", "banana", "naranja"]
for fruta in frutas:
    print(fruta)

def saludar(persona):
    return f"Hola, {persona}!"

print(saludar(nombre))
```

Python usa la indentación para agrupar instrucciones; normalmente se usan
cuatro espacios. Un diccionario guarda datos con nombre:

```python
asociado = {"nombre": "Luz", "numero": 123, "activo": True}
print(asociado["nombre"])
```

Ejercicio: pedir tres notas, calcular el promedio y mostrar si la persona
aprobó con una nota mínima de 6.

## 4. Un proyecto Python con uv

```powershell
mkdir mi-proyecto
cd mi-proyecto
uv init
uv run python main.py
uv add requests
```

`uv` crea y administra el entorno virtual. En Uni2 se usa `uv sync` para
instalar lo que figura en `pyproject.toml` y `uv run ...` para ejecutar
comandos dentro del entorno del proyecto.

## 5. ¿Qué es Django?

Django es un framework web escrito en Python. Sus piezas principales son:

- **Modelos:** datos que se guardan en la base.
- **URLs:** direcciones de la aplicación.
- **Vistas:** reciben pedidos y preparan respuestas.
- **Templates:** HTML con datos dinámicos.
- **Migraciones:** cambios controlados en la estructura de la base.
- **Apps:** módulos separados por responsabilidad.

En Uni2, `usuarios`, `gestion`, `asociados`, `comercios` y `cuotas` son apps
Django separadas.

La documentación oficial incluye una
[guía para Windows](https://docs.djangoproject.com/en/6.0/howto/windows/) y
un [tutorial paso a paso](https://docs.djangoproject.com/en/6.0/intro/tutorial01/).

## 6. Mini tutorial Django

Este ejercicio es independiente de Uni2:

```powershell
mkdir mi-sitio
cd mi-sitio
uv init
uv add django
uv run django-admin startproject config .
uv run python manage.py runserver
```

Abrir <http://127.0.0.1:8000/>. Detener el servidor con `Ctrl+C`.

Crear una app:

```powershell
uv run python manage.py startapp saludo
```

Agregar `saludo` a `INSTALLED_APPS` en `config/settings.py`. En
`saludo/views.py` escribir:

```python
from django.http import HttpResponse


def inicio(request):
    return HttpResponse("Hola desde mi app Django")
```

Crear `saludo/urls.py`:

```python
from django.urls import path
from . import views

urlpatterns = [path("", views.inicio, name="inicio")]
```

En `config/urls.py`, agregar `include` y esta ruta:

```python
from django.urls import include, path

urlpatterns = [path("saludo/", include("saludo.urls"))]
```

Abrir <http://127.0.0.1:8000/saludo/>.

## 7. Preparar Uni2

Instalar Git, clonar el repositorio y ejecutar:

```powershell
git clone git@github.com:CET-3/uni2.git
cd uni2
uv sync
Copy-Item .env.example .env
uv run python manage.py migrate
uv run python manage.py carga_inicial
uv run python manage.py runserver
```

Abrir <http://127.0.0.1:8000/>.

Usuarios ficticios locales:

| Perfil | Usuario | Contraseña |
|---|---|---|
| Gestión/admin técnico | `admin` | `admin1234` |
| Atención de mutual | `atencion` | `atencion1234` |
| Asociado | `asociado` | `asociado1234` |
| Comercio | `comercio` | `comercio1234` |

La base local es `db.sqlite3`; no se sube a Git.

## 8. Primer cambio en Uni2

No trabajar directamente sobre `main` ni `staging`:

```powershell
git switch staging
git pull --ff-only
git switch -c nombre-del-cambio
```

Después de programar:

```powershell
$env:DB_ENGINE = "sqlite"
uv run pytest
git add archivo1.py archivo2.html
git commit -m "Agrega descripcion breve"
git push -u origin nombre-del-cambio
```

Abrir un Pull Request hacia `staging`. Las decisiones funcionales o de
arquitectura también deben actualizar `especificacion/`.

## Problemas frecuentes

**`uv` no se reconoce:** cerrar y volver a abrir PowerShell.

**El puerto 8000 está ocupado:**

```powershell
uv run python manage.py runserver 8001
```

**Se modificó un modelo:**

```powershell
uv run python manage.py makemigrations
uv run python manage.py migrate
```

No ejecutar `carga_inicial` sobre staging ni producción.
