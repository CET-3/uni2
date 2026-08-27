import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]


def load_dotenv(dotenv_path: Path):
    if not dotenv_path.exists():
        return

    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


load_dotenv(BASE_DIR / ".env")

SECRET_KEY = "dev-secret-key"
DEBUG = False
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "web",
    "usuarios",
    "gestion",
    "auditoria",
    "comunicaciones",
    "asociados",
    "cuotas",
    "comercios",
    "contenidos",
    "pwa",
    "especificacion",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "pwa.middleware.PWACacheControlMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "config.context_processors.google_analytics",
                "usuarios.context_processors.navigation_roles",
                "pwa.context_processors.pwa_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DB_ENGINE = os.getenv("DB_ENGINE", "sqlite")

if DB_ENGINE == "postgres":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME", "uni2"),
            "USER": os.getenv("DB_USER", "postgres"),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", "127.0.0.1"),
            "PORT": os.getenv("DB_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = []

ALLOW_DEMO_DATA = False

LANGUAGE_CODE = "es-ar"
TIME_ZONE = "America/Argentina/Buenos_Aires"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Las URLs de credenciales contienen un UUID privado. No deben viajar como
# referente cuando la persona sigue enlaces hacia otro origen.
SECURE_REFERRER_POLICY = "same-origin"

# La PWA usa un identificador de build para separar sus cachés. Los deploys
# automáticos de Vercel exponen el SHA; el workflow de staging lo pasa de forma
# explícita porque ese proyecto no está conectado al repositorio.
PWA_BUILD_ID = (
    os.getenv("PWA_BUILD_ID")
    or os.getenv("VERCEL_GIT_COMMIT_SHA")
    or "development"
)
PWA_CREDENTIAL_OFFLINE_TTL_DAYS = 7
PWA_PRIVATE_DATA_EPOCH = os.getenv("UNI2_PRIVATE_DATA_EPOCH", "development")
PWA_APP_NAME = "UNI2 - Mutual Escolar"
PWA_SHORT_NAME = "UNI2"
PWA_DESCRIPTION = "Gestión y servicios de la Mutual Escolar del CET 3."
PWA_THEME_COLOR = "#3f51b5"
PWA_THEME_COLOR_LIGHT = "#f7f9fc"
PWA_THEME_COLOR_DARK = "#080c16"
PWA_BACKGROUND_COLOR = "#f7f9fc"
PWA_ICON_DIRECTORY = "pwa/icons"

# Los templates usan estas variables para que un entorno no productivo sea
# inequívoco, incluso dentro de la pantalla offline cacheada.
UNI2_DEPLOYMENT_ENVIRONMENT = "development"
UNI2_ENVIRONMENT_LABEL = ""
UNI2_ENVIRONMENT_SHORT_LABEL = ""

# Analytics queda apagado por defecto. Solamente Producción puede leer el ID
# real; staging lo vuelve a deshabilitar luego de heredar el perfil productivo.
GOOGLE_ANALYTICS_MEASUREMENT_ID = ""

# Las integraciones todavía no están implementadas. Declarar la política desde
# ahora evita que staging herede por accidente proveedores reales en el futuro.
UNI2_TRANSACTIONAL_EMAIL_MODE = "disabled"
UNI2_BATCH_EMAIL_MODE = "disabled"
UNI2_WEB_PUSH_MODE = "disabled"
UNI2_SITE_URL = os.getenv("UNI2_SITE_URL", "http://localhost:8000").rstrip("/")
DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL", "UNI2 <no-responder@example.com>"
)
UNI2_SOLICITUD_TOKEN_TTL_DAYS = 30
UNI2_SOLICITUD_CREACION_MAX_INTENTOS = 30
UNI2_SOLICITUD_CREACION_VENTANA_MINUTOS = 10
UNI2_SOLICITUD_CORRECCION_MAX_INTENTOS = 5
UNI2_SOLICITUD_CORRECCION_VENTANA_MINUTOS = 60
UNI2_TRUST_VERCEL_CLIENT_IP = False

# El admin técnico puede recibir acciones masivas sobre muchas cuotas luego de
# importaciones iniciales. El valor por defecto de Django queda corto para ese uso.
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000
