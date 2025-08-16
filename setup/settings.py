import os
from pathlib import Path
import dj_database_url

from django.contrib.messages import constants as messages
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / "subdir".
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/
SECRET_KEY = str(os.getenv("DJANGO_SECRET_KEY"))
DEBUG = True
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]
SITE_ID = 1

# Application definition
INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "whitenoise.runserver_nostatic",
    "django_extensions",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.oauth2",
    "apps.users.providers.fortytwo",
    "rosetta",
    "channels",
    "apps.users.apps.UsersConfig",
    "apps.matchmaking.apps.MatchmakingConfig",
    "apps.chat.apps.ChatConfig",
]
MIDDLEWARE = [
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]
ROOT_URLCONF = "setup.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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
ASGI_APPLICATION = "setup.asgi.application"
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_URL = os.getenv("REDIS_URL", None)

if REDIS_URL:
    redis_hosts = [REDIS_URL]
elif REDIS_PASSWORD:
    redis_hosts = [(f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0")]
else:
    redis_hosts = [(REDIS_HOST, REDIS_PORT)]

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": redis_hosts,
        },
    },
}

# Authentication
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
ACCOUNT_LOGIN_ON_SIGNUP = False
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
SOCIALACCOUNT_PROVIDERS = {
    "fortytwo": {
        "APP": {
            "client_id": str(os.getenv("CLIENT_ID_42")),
            "secret": str(os.getenv("SECRET_42")),
        },
    },
}

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
import dj_database_url

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=True)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB"),
            "USER": os.getenv("POSTGRES_USER"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
            "HOST": "db",
            "PORT": 5432,
        },
    }

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators
AUTH_USER_MODEL = "users.User"
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
# https://docs.djangoproject.com/en/5.1/topics/i18n/
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True
LANGUAGES = [
    ("pt-br", _("Português")),
    ("en", _("Inglês")),
    ("es", _("Espanhol")),
]
LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale"),
]

# Configurações de arquivos estáticos
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

# Configurações de arquivos de mídia
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Configure o WhiteNoise para servir os arquivos estáticos comprimidos
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Messages
MESSAGE_TAGS = {
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}

LOGIN_URL = "login"
CSRF_TRUSTED_ORIGINS = ["https://transcendence.up.railway.app"]
ALLOWED_HOSTS = ["*"]
CORS_ALLOW_CREDENTIALS = True
