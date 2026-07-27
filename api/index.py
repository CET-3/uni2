import os
import sys

# Vercel ejecuta este archivo como punto de entrada de la función serverless.
# La inicialización operativa de la base se realiza mediante comandos explícitos.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

from config.wsgi import application  # noqa: E402, F401
