import os
from pathlib import Path
from datetime import timedelta
from typing import Any
import django.urls

def monkeypatch_ninja_uuid_converter() -> None:
    """
    Monkeypatch to fix Django-Ninja UUID converter warning.
    Reference: https://github.com/vitalik/django-ninja/issues/1266
    """
    import importlib
    import sys

    module_name = "ninja.signature.utils"
    sys.modules.pop(module_name, None)

    original_register_converter = django.urls.register_converter

    def fake_register_converter(*_: Any, **__: Any) -> None:
        pass

    django.urls.register_converter = fake_register_converter
    importlib.import_module(module_name)

    django.urls.register_converter = original_register_converter

def configure_pydantic_warnings() -> None:
    """
    Configure warnings to suppress Pydantic V2 deprecation warnings from Django-Ninja.
    """
    import warnings
    
    warnings.filterwarnings(
        "ignore", 
        message="Support for class-based.*config.*is deprecated.*use ConfigDict instead",
        category=DeprecationWarning
    )
    
    warnings.filterwarnings(
        "ignore",
        category=UserWarning,
        module="pydantic._internal._config"
    )

configure_pydantic_warnings()

monkeypatch_ninja_uuid_converter()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-#df8_cboq=a083mza$o0g!ua0-4m5nxh!3uyf-^_-b-_bk82pf')
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes', 'on')
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ninja',
    'jobs',
    'user_auth',
    'corsheaders',
]

# 設定 crontab 日誌檔路徑
CRONTAB_DJANGO_PROJECT_LOGS_PATH = '/home/eric/code/exercise/backend/'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'job_platform.urls'
WSGI_APPLICATION = 'job_platform.wsgi.application'

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'db.sqlite3',
  }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

NINJA_JWT = {
  'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
  'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
  'ALGORITHM': 'HS256',
  'SIGNING_KEY': SECRET_KEY,
}

LOGGING = {
  'version': 1,
  'disable_existing_loggers': False,
  'formatters': {
    'verbose': {
      'format': '{levelname} {asctime} {module} {message}',
      'style': '{',
    },
    'simple': {
      'format': '{levelname} {message}',
      'style': '{',
    },
  },
  'handlers': {
    'console': {
      'level': 'DEBUG',
      'class': 'logging.StreamHandler',
      'formatter': 'verbose',
    },
    'file': {
      'level': 'DEBUG',
      'class': 'logging.FileHandler',
      'filename': 'debug.log',
      'formatter': 'verbose',
    },
    'job_status_file': {
      'level': 'INFO',
      'class': 'logging.FileHandler',
      'filename': 'job_status_scheduler.log',
      'formatter': 'verbose',
    },
  },
  'loggers': {
    'jobs': {
      'handlers': ['console', 'file'],
      'level': 'DEBUG',
      'propagate': True,
    },
    'jobs.management.commands.update_job_status': {
      'handlers': ['console', 'file', 'job_status_file'],
      'level': 'INFO',
      'propagate': False,
    },
  },
  'root': {
    'handlers': ['console'],
    'level': 'WARNING',
  },
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Optional: Allow all origins (less secure, for development only)
# CORS_ALLOW_ALL_ORIGINS = True

# Optional: Allow specific headers
# CORS_ALLOW_HEADERS = [
#     'authorization',
#     'content-type',
# ]

# Optional: Allow specific methods
# CORS_ALLOW_METHODS = [
#     'DELETE',
#     'GET',
#     'OPTIONS',
#     'PATCH',
#     'POST',
#     'PUT',
# ]
