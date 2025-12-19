"""
Settings module initialization.
Import base settings and override with environment-specific settings.
"""
from decouple import config, Csv

# Определяем окружение (development или production)
ENVIRONMENT = config('ENVIRONMENT', default='development')

if ENVIRONMENT == 'production':
    from .production import *
else:
    from .base import *

