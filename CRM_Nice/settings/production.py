from __future__ import annotations

from .base import *  # noqa: F401,F403

import dj_database_url


DEBUG = False

SECRET_KEY = env("SECRET_KEY")  # у production обов'язково через env
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[".onrender.com"])


# PostgreSQL від Render через DATABASE_URL (якщо є)
# Якщо DATABASE_URL не встановлено, використовуємо SQLite
database_url = env("DATABASE_URL", default=None)

if database_url:
    DATABASES = {
        "default": dj_database_url.config(
            default=database_url,
            conn_max_age=600,
            ssl_require=True
        ),
    }
else:
    # Fallback до SQLite (не рекомендується для production, але працює)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True


# Static files (WhiteNoise)
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=["https://*.onrender.com"],
)

