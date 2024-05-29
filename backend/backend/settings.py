import locale
from pathlib import Path

import environ
from borb.pdf.canvas.font.simple_font.true_type_font import TrueTypeFont
from dotenv import find_dotenv

env = environ.Env()
if DEBUG := env.bool("DEBUG", default=True):
    environ.Env.read_env(find_dotenv(".env", raise_error_if_not_found=True))

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env.str("SECRET_KEY")

ALLOWED_HOSTS = []


INSTALLED_APPS = [
    "core.apps.CoreConfig",
    "salary.apps.SalaryConfig",
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
        "HOST": env.str("POSTGRES_HOST", "db"),
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

USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")

TELEGRAM_TOKEN = env.str("TELEGRAM_TOKEN", "")
CHECK_MAIL = env.str("CHECK_MAIL", False)
INTERVAL = env.int("INTERVAL", 60)

SITE_URL = env.str("SITE_URL")
SITE_NAME = env.str("SITE_NAME")
SITE_PASSWORD = env.str("SITE_PASSWORD")

CUSTOM_FONT = TrueTypeFont.true_type_font_from_file(
    Path("files/Source Serif Pro.ttf")
)
