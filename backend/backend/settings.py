import locale
import os
from pathlib import Path

import environ
from borb.pdf.canvas.font.simple_font.true_type_font import TrueTypeFont
from dotenv import find_dotenv

env = environ.Env()

DEBUG = env.bool("DEBUG", default=True)
if DEBUG:
    environ.Env.read_env(find_dotenv(".env", raise_error_if_not_found=True))

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env.str("SECRET_KEY")

CSRF_TRUSTED_ORIGINS = [
    "http://localhost",
    "https://" + env.str("MY_NAME"),
    "http://" + env.str("MY_NAME"),
]
ALLOWED_HOSTS = CSRF_TRUSTED_ORIGINS


INSTALLED_APPS = [
    "core.apps.CoreConfig",
    "salary.apps.SalaryConfig",
    "report.apps.ReportConfig",
    "stock.apps.StockConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"

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

WSGI_APPLICATION = "backend.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": env.str("POSTGRES_HOST", "127.0.0.1"),
        "NAME": env.str("POSTGRES_NAME", "postgres"),
        "USER": env.str("POSTGRES_USER", "postgres"),
        "PASSWORD": env.str("POSTGRES_PASSWORD", "postgres"),
        "PORT": env.int("POSTGRES_PORT", "5432"),
    }
}


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


LANGUAGE_CODE = "ru"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = False

STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(BASE_DIR, "static")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")

TELEGRAM_TOKEN = env.str("TELEGRAM_TOKEN", "")
CHECK_MAIL = env.bool("CHECK_MAIL", False)
TEST_MAIL = env.bool("TEST_MAIL", False)
INTERVAL = env.int("INTERVAL", 60)

IMAP_SSL_HOST = env.str("IMAP_SSL_HOST", "")
IMAP_USERNAME = env.str("IMAP_USERNAME", "")
IMAP_PASSWORD = env.str("IMAP_PASSWORD", "")
IMAP_FROM_EMAIL = env.str("IMAP_FROM_EMAIL", "")

REDIS_HOST = env.str("REDIS_HOST", "")
REDIS_PORT = env.str("REDIS_PORT", "")
SITE_URL = env.str("SITE_URL")
SITE_NAME = env.str("SITE_NAME")
SITE_PASSWORD = env.str("SITE_PASSWORD")

CUSTOM_FONT = TrueTypeFont.true_type_font_from_file(
    Path("files/Source Serif Pro.ttf")
)
