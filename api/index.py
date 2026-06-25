import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

import django

django.setup()

from django.db import connection, close_old_connections  # noqa: E402

# Migración automática: solo corre si la columna foto no existe.
# Hecho así para no tener que extraer DATABASE_URL del entorno
# encriptado de Vercel y poder mantener migrate manual como
# excepción de la regla general.
with connection.cursor() as cursor:
    cursor.execute(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name='comercios_comercio' AND column_name='foto'"
    )
    if not cursor.fetchone():
        from django.core.management import call_command  # noqa: E402

        call_command("migrate", interactive=False, verbosity=0)
        call_command("carga_inicial")

close_old_connections()

from config.wsgi import application  # noqa: E402, F401
