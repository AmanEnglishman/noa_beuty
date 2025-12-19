"""
Local development Django settings for config project.
Настройки для локальной разработки.
"""

from .base import *
from decouple import config, Csv

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,0.0.0.0', cast=Csv())

# Database
# Используем SQLite для локальной разработки
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email backend для разработки (вывод в консоль)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Django Jazzmin (улучшенная админка)
JAZZMIN_SETTINGS = {
        "site_title": "NOA Beauty Admin",
        "site_header": "NOA Beauty",
        "site_brand": "NOA Beauty",
        "site_logo": None,
        "login_logo": None,
        "login_logo_dark": None,
        "site_logo_classes": "img-circle",
        "site_icon": None,
        "welcome_sign": "Добро пожаловать в панель управления NOA Beauty",
        "copyright": "NOA Beauty",
        "search_model": ["auth.User", "products.Perfume", "sales.Sale"],
        "user_avatar": None,
        "topmenu_links": [
            {"name": "Главная", "url": "admin:index", "permissions": ["auth.view_user"]},
            {"name": "Сайт", "url": "/", "new_window": True},
        ],
        "usermenu_links": [
            {"name": "Сайт", "url": "/", "new_window": True},
        ],
        "show_sidebar": True,
        "navigation_expanded": True,
        "hide_apps": [],
        "hide_models": [],
        "order_with_respect_to": ["auth", "products", "inventory", "sales", "finance"],
        "custom_links": {
            "sales": [{
                "name": "Продажи сегодня",
                "url": "/sales/today/",
                "icon": "fas fa-shopping-cart",
                "new_window": True,
            }]
        },
        "icons": {
            "auth": "fas fa-users-cog",
            "auth.user": "fas fa-user",
            "auth.Group": "fas fa-users",
            "products.Brand": "fas fa-tags",
            "products.Perfume": "fas fa-spray-can",
            "products.CosmeticProduct": "fas fa-palette",
            "products.BottleType": "fas fa-wine-bottle",
            "inventory.PerfumeStock": "fas fa-boxes",
            "inventory.BottleStock": "fas fa-box",
            "inventory.CosmeticStock": "fas fa-archive",
            "sales.Sale": "fas fa-receipt",
            "sales.SaleItem": "fas fa-shopping-basket",
            "sales.Expense": "fas fa-money-bill-wave",
            "sales.Income": "fas fa-money-check-alt",
            "finance": "fas fa-chart-line",
        },
        "default_icon_parents": "fas fa-chevron-circle-right",
        "default_icon_children": "fas fa-circle",
        "related_modal_active": False,
        "custom_css": None,
        "custom_js": None,
        "use_google_fonts_cdn": True,
        "show_ui_builder": False,
        "changeform_format": "horizontal_tabs",
        "changeform_format_overrides": {
            "auth.user": "collapsible",
            "auth.group": "vertical_tabs",
        },
    }

# Логирование для разработки
# Уровень логирования SQL-запросов (можно изменить через LOG_SQL_QUERIES в .env)
LOG_SQL_QUERIES = config('LOG_SQL_QUERIES', default=False, cast=bool)
DJANGO_LOG_LEVEL = config('DJANGO_LOG_LEVEL', default='INFO')
APP_LOG_LEVEL = config('APP_LOG_LEVEL', default='DEBUG')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
        'sql': {
            'format': 'SQL {duration:.3f}s: {sql}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'filters': ['require_debug_true'],
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'file_sql': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'sql.log',
            'formatter': 'sql',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': DJANGO_LOG_LEVEL,
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': DJANGO_LOG_LEVEL,
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['file_sql'] if LOG_SQL_QUERIES else [],
            'level': 'DEBUG' if LOG_SQL_QUERIES else 'WARNING',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'sales': {
            'handlers': ['console', 'file'],
            'level': APP_LOG_LEVEL,
            'propagate': False,
        },
        'inventory': {
            'handlers': ['console', 'file'],
            'level': APP_LOG_LEVEL,
            'propagate': False,
        },
        'products': {
            'handlers': ['console', 'file'],
            'level': APP_LOG_LEVEL,
            'propagate': False,
        },
        'finance': {
            'handlers': ['console', 'file'],
            'level': APP_LOG_LEVEL,
            'propagate': False,
        },
    },
}

# Создаём директорию для логов если её нет
import os
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# Настройки для разработки
# Отключаем некоторые проверки безопасности для удобства разработки
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
X_FRAME_OPTIONS = 'SAMEORIGIN'  # Разрешаем iframe для разработки

# Кэширование (используем простой кэш в памяти для разработки)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Настройки сессий для разработки
SESSION_COOKIE_AGE = 86400  # 24 часа
SESSION_SAVE_EVERY_REQUEST = True

# Настройки для работы со статикой в dev режиме
# Django будет автоматически обслуживать статику через runserver
# STATICFILES_DIRS можно добавить если нужны дополнительные директории

# Настройки для работы с медиа файлами
# В production это будет обслуживаться через nginx

# Отключение проверки паролей для удобства разработки (опционально)
# AUTH_PASSWORD_VALIDATORS = []  # Раскомментируйте если нужно

# Настройки для печати чеков (если используется)
PRINTER_CONFIG = {
    'enabled': config('PRINTER_ENABLED', default=False, cast=bool),
    'driver': config('PRINTER_DRIVER', default='file'),  # file, usb, network
    'device': config('PRINTER_DEVICE', default='/dev/usb/lp0'),
}

# Настройки для генерации штрихкодов и QR-кодов
BARCODE_CONFIG = {
    'format': config('BARCODE_FORMAT', default='CODE128'),
    'size': (100, 50),
}

QRCODE_CONFIG = {
    'version': 1,
    'error_correction': 'M',
    'box_size': 10,
    'border': 4,
}

