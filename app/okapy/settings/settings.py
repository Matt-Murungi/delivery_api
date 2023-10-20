import os
import firebase_admin
from firebase_admin import credentials
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", True)

SITE_ID = 1

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_CREDENTIALS = True

CORS_EXPOSE_HEADERS = [
    "Set-Cookie",
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "admin_honeypot",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "corsheaders",
    "channels",
    "users",
    "partners",
    "chats",
    "core",
    "vehicles",
    "feedback",
    "bookings",
    "payments",
    "admins",
    "fcm_django",
    "notifications",
    "custom_auth",
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "rest_auth",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "rest_auth.registration",
    "drf_yasg",
    "widget_tweaks",
]

AUTH_USER_MODEL = "users.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "bdeliv.urls"

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

TEMPLATE_CONTEXT_PROCESSORS = "django.core.context_processors.static"

WSGI_APPLICATION = "bdeliv.wsgi.application"

# channels
ASGI_APPLICATION = "bdeliv.routing.application"

REDIS_SERVER_IP = os.environ.get("REDIS_SERVER_IP")

REDIS_HOST = f"redis://{REDIS_SERVER_IP}:6380/1"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [REDIS_HOST]},
    }
}

# migrated the database

# DEVELOPMENT CONFIG
# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {
#             'hosts': [('127.0.0.1', 6379)]
#         },
#     }
# }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

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

FCM_DJANGO_SETTINGS = {
    "FCM_SERVER_KEY": "AAAAIUpdhts:APA91bEyYeCpSWB8sU_6xpAlsEatqCI1rPsyjdOmRt62Hb50YUIvbBamfdkwJThHmBaqG1orAyveBHQOWS6pZa9U_KpHTFPeykTBGuj24G86hbpAIjfOaS0-gYeCDvsaPN5lBP5Z9jyK",
    # "Update of device with duplicate registration ID" for more details.
    "UPDATE_ON_DUPLICATE_REG_ID": True,
}

# internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Nairobi"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# static
MEDIA_URL = "/media/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles/")
STATIC_URL = "/static/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static/"),
]

# email
email_host = os.environ.get("EMAIL_HOST_USER")
default_from_email = f"bdeliv <noreply{email_host}>"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = email_host
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
# EMAIL_USE_SSL: False
DEFAULT_FROM_EMAIL = default_from_email

# allauth
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
    "custom_auth.auth_backends.PasswordlessAuthBackend",
)
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"

# rest framework
REST_FRAMEWORK = {
    "DATETIME_FORMAT": "%m/%d/%Y %H:%M:%S",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
}

# rest auth
REST_AUTH_REGISTER_SERIALIZERS = {
    "REGISTER_SERIALIZER": "users.serializers.UserRegistrationSerializer",
}

REST_AUTH_SERIALIZERS = {
    "USER_DETAILS_SERIALIZER": "users.serializers.UserSerializer",
    "LOGIN_SERIALIZER": "users.serializers.LoginSerializer",
    "PASSWORD_RESET_SERIALIZER": "users.serializers.PasswordSerializer",
}

LOGOUT_ON_PASSWORD_CHANGE = False
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
APPEND_SLASHES = False
OLD_PASSWORD_FIELD_ENABLED = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Settings files for different environments
try:
    environment = os.environ["ENVIRONMENT"]
except KeyError:
    environment = "staging"
if environment == "staging":
    from .staging import *
elif environment == "production":
    from .production import *
else:
    from .local import *


ORDER_STATUS = (
    ("1", "created"),
    ("2", "confirmed"),
    ("3", "picked"),
    ("4", "transit"),
    ("5", "arrived"),
    ("6", "partner_created"),
    ("7", "partner_confirmed"),
    ("8", "rejected"),
)

cred = credentials.Certificate(os.path.join(BASE_DIR, "./bdeliv/user_app_cred.json"))
firebase_admin.initialize_app(cred)
