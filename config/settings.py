from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "domen.com",
    "www.domen.com",
    "2t6cc8-77-91-65-140.ru.tuna.am",
]

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "corsheaders",
    "django_filters",
]

LOCAL_APPS = [
    "apps.common",
    "apps.main",
    "apps.orders",
    "apps.payment",
    "apps.storage",
    "apps.contacts",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
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
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": config("DB_ENGINE", default="django.db.backends.sqlite3"),
        "NAME": config("DB_NAME", default=str(BASE_DIR / "db.sqlite3")),
        "USER": config("DB_USER", default=""),
        "PASSWORD": config("DB_PASSWORD", default=""),
        "HOST": config("DB_HOST", default=""),
        "PORT": config("DB_PORT", default=""),
    }
}

# Добавляем специфичные настройки для каждой БД
if DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3":
    # SQLite: увеличиваем timeout для уменьшения "database is locked" ошибок
    DATABASES["default"]["OPTIONS"] = {
        "timeout": 20,  # Ждём до 20 секунд перед ошибкой
    }
elif DATABASES["default"]["ENGINE"].startswith("django.db.backends.postgresql"):
    # PostgreSQL: настройки подключения
    DATABASES["default"]["OPTIONS"] = {
        "connect_timeout": 10,
    }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "ru-RU"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Additional locations of static files (только если директория существует)
STATICFILES_DIRS = []

# Проверяем, существует ли директория static в проекте
if (BASE_DIR / "static").exists():
    STATICFILES_DIRS.append(BASE_DIR / "static")

# Static files finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Yandex Cloud Object Storage
YANDEX_STORAGE_ACCESS_KEY = config("YANDEX_STORAGE_ACCESS_KEY", default="")
YANDEX_STORAGE_SECRET_KEY = config("YANDEX_STORAGE_SECRET_KEY", default="")
YANDEX_STORAGE_BUCKET_NAME = config("YANDEX_STORAGE_BUCKET_NAME", default="")
YANDEX_STORAGE_ENDPOINT = config(
    "YANDEX_STORAGE_ENDPOINT", default="https://storage.yandexcloud.net"
)
YANDEX_STORAGE_REGION = config("YANDEX_STORAGE_REGION", default="ru-central1")

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework Configuration
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ],
    # Rate limiting
    "DEFAULT_THROTTLE_RATES": {
        "order_create": "5/minute",  # Создание заказов
        "contact_form": "3/hour",  # Контактная форма
        "webhook": "100/minute",  # Вебхуки платежей
    },
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Укажите порт, на котором работает ваш Vue.js
    "http://127.0.0.1:5173",
    "https://domen.com",
    "https://www.domen.com",
]

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"


# Yookassa Settings
YOOKASSA_ACCOUNT_ID = config("YOOKASSA_ACCOUNT_ID", default="")
YOOKASSA_SECRET_KEY = config("YOOKASSA_SECRET_KEY", default="")


# URL фронтенда для редиректов
FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:5173")

# Email настройки (для уведомлений)
EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = config("EMAIL_HOST", default="localhost")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=False, cast=bool)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", default=False, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="Minem <noreply@minem.com>")

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs/app.log",
            "maxBytes": 10485760,
            "backupCount": 5,
            "formatter": "verbose",
            "encoding": "utf-8",
        },
        "payment_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs/payments.log",
            "maxBytes": 10485760,
            "backupCount": 5,
            "formatter": "verbose",
            "encoding": "utf-8",
        },
        "storage_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs/storage.log",
            "maxBytes": 10485760,
            "backupCount": 5,
            "formatter": "verbose",
            "encoding": "utf-8",
        },
        "email_file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs/email.log",
            "maxBytes": 10485760,
            "backupCount": 5,
            "formatter": "verbose",
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "apps.payment": {
            "handlers": ["payment_file"],
            "level": "INFO",
            "propagate": False,
        },
        "apps.orders": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": False,
        },
        "apps.orders.services.email_service": {
            "handlers": ["email_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "apps.storage": {
            "handlers": ["storage_file"],
            "level": "INFO",
            "propagate": False,
        },
        "django.core.mail": {
            "handlers": ["email_file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
