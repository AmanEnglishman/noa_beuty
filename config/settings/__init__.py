"""
Settings module initialization.
Import base settings and override with environment-specific settings.
"""
from decouple import config, Csv
import os

# Определяем окружение (development, local или production)
ENVIRONMENT = config('ENVIRONMENT', default='local')

if ENVIRONMENT == 'production':
    from .production import *
elif ENVIRONMENT == 'local' or ENVIRONMENT == 'development':
    try:
        from .local import *
    except ImportError:
        # Если local.py не существует, используем base.py
        from .base import *
else:
    # По умолчанию используем base.py
    from .base import *

