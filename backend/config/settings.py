"""
Django settings for the Candle Shop backend.

All environment-specific values are read from environment variables
(or a local `.env` file). See `.env.example` for the available keys.
"""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    CORS_ALLOWED_ORIGINS=(list, []),
    CSRF_TRUSTED_ORIGINS=(list, []),
    BEHIND_PROXY=(bool, False),
    SERVE_MEDIA=(bool, False),
)
environ.Env.read_env(BASE_DIR / ".env")

# No default on purpose: the app refuses to start without a SECRET_KEY.
SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party
    "rest_framework",
    "corsheaders",
    # Local
    "shop",
    "home",
    "care",
    "ingredients",
    "decorate",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Serves static files and the built React app when DEBUG is off.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
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
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# Defaults to SQLite. To switch to PostgreSQL, set DATABASE_URL in .env, e.g.
#   DATABASE_URL=postgres://user:password@localhost:5432/candleshop
# (and `pip install "psycopg[binary]"`).

DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
}


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static & media files

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

# The built React app (`npm run build` in ../frontend). When present, Django serves it
# at the site root, so the whole shop runs from one address (see deploy/README.md).
FRONTEND_DIST = Path(env("FRONTEND_DIST", default=str(BASE_DIR.parent / "frontend" / "dist")))
if FRONTEND_DIST.is_dir():
    WHITENOISE_ROOT = FRONTEND_DIST
# Vite puts a content hash in every file under /assets/, so they can be cached forever.
WHITENOISE_IMMUTABLE_FILE_TEST = r"^/assets/"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Django REST Framework

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 12,
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
}


# CORS (React dev server)

CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")


# Public hosting (deploy/start-public.ps1 sets these)

# Origins allowed to POST forms such as the admin login, e.g. https://*.trycloudflare.com
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")

# Behind an HTTPS tunnel/proxy: trust its forwarded protocol and host, so links and image
# URLs use the public https address. Only enable when the server isn't reachable directly.
if env("BEHIND_PROXY"):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    USE_X_FORWARDED_HOST = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Serve uploaded images from Django itself when DEBUG is off (fine for a small shop on
# one machine; a bigger setup would use a web server or cloud storage instead).
SERVE_MEDIA = env("SERVE_MEDIA")
