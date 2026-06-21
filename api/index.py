import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

import django
from django.core.management import call_command

django.setup()
call_command("migrate", "--noinput")

from config.wsgi import application  # noqa: E402, F401
