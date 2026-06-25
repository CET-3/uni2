import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

import django

django.setup()

# Correr migraciones automáticamente en el frío inicio.
# Django salta las ya aplicadas, así que es seguro en cada deploy.
from django.core.management import call_command  # noqa: E402

call_command("migrate", interactive=False, verbosity=0)

from config.wsgi import application  # noqa: E402, F401
