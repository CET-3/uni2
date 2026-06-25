import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

import django

django.setup()

# DEBUG: obtener DATABASE_URL de producción
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dbg")
db_url = os.environ.get("DATABASE_URL", "no-encontrada")
logger.info("=== DB_URL: %s", db_url)

from config.wsgi import application  # noqa: E402, F401
