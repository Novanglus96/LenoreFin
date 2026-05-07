# flake8: noqa: F403,F401
import os

os.environ.setdefault("DEBUG", "0")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("DJANGO_ALLOWED_HOSTS", "localhost 127.0.0.1")
os.environ.setdefault("CSRF_TRUSTED_ORIGINS", "http://localhost")
os.environ.setdefault("TIMEZONE", "America/New_York")

from backend.settings import *

VITE_API_KEY = "test-api-key"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "CRITICAL",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "CRITICAL",
    },
}
