from pathlib import Path
import os
import sys
from datetime import timedelta

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv
from django.utils import timezone
SPATIALITE_LIBRARY_PATH = 'mod_spatialite'
# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured("SECRET_KEY environment variable is missing")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.gis',  # Add this before your app
    'leaflet',  # Add this
    'rest_framework_gis',  # Add this

    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'phonenumber_field',
    'accounts.apps.AccountsConfig',
    'base.apps.BaseConfig',

    'django_filters',
    'channels',
]

_BASE_MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # This should be at the top
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',

]

# Check if we're running under ASGI
if os.environ.get('RUNNING_ASGI') == 'True':
    # For ASGI (Channels), use only the Django middleware
    MIDDLEWARE = _BASE_MIDDLEWARE
else:
    # For WSGI (regular Django), include all middleware
    MIDDLEWARE = _BASE_MIDDLEWARE + [
        'accounts.middleware.RequestResponseLoggingMiddleware',
        'accounts.middleware.LoginTrackingMiddleware',
        'accounts.middleware.FormSubmissionLoggingMiddleware',
    ]

AUTHENTICATION_BACKENDS = [
    'accounts.auth.UUIDModelBackend',  # Our custom backend
    'django.contrib.auth.backends.ModelBackend',  # Default backend
]

ROOT_URLCONF = 'back.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                # Remove this line for the custom roles: 'base.context_processors.user_roles'
                # 'base.context_processors.user_roles',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'back.wsgi.application'
ASGI_APPLICATION = 'back.asgi.application'

# Database
DATABASES = {
    'default': {
        # Must be this, not 'django.db.backends.sqlite3'
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        # 'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

SPATIALITE_LIBRARY_PATH = 'mod_spatialite'


# If you want to use a different database, uncomment this and set environment variables
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.getenv('DB_NAME', 'mydatabase'),
#         'USER': os.getenv('DB_USER', 'dbuser'),
#         'PASSWORD': os.getenv('DB_PASSWORD', ''),
#         'HOST': os.getenv('DB_HOST', 'localhost'),
#         'PORT': os.getenv('DB_PORT', '5432'),
#     }
# }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]



# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}


LEAFLET_CONFIG = {
    # Saudi Arabia coordinates (adjust as needed)
    'DEFAULT_CENTER': (24.6897, 46.7172),
    'DEFAULT_ZOOM': 6,
    'MIN_ZOOM': 4,
    'MAX_ZOOM': 18,
    'TILES': [('OpenStreetMap', 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        'attribution': '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    })],
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Required directories
REQUIRED_DIRS = [
    os.path.join(BASE_DIR, 'media'),
    os.path.join(BASE_DIR, 'staticfiles'),
]

# CORS settings - allow all origins for development
CORS_ALLOW_ALL_ORIGINS = True
# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5137",
    "http://localhost:5173",  # Default SvelteKit dev server
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5137",
]

CORS_ALLOW_CREDENTIALS = True  # Required for cookies/authentication to work
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "x-request-id",
    "x-debug",  # Allow your custom debug header
]

# For development, you can use this instead of specifying individual origins
# Only use this in development, not in production
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True

# Email settings - using your working .env values
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)


FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")

# Add this to settings.py
EMAIL_USE_SSL = True
EMAIL_PORT = 465  # Change port for SSL
EMAIL_USE_TLS = False  # Disable TLS when using SSL

# Production settings
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'accounts.CustomUser'

# Define server timezone for more predictable timestamps
SERVER_TIMEZONE = timezone


# Channel layers configuration - keeping the existing InMemoryChannelLayer
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
        # For production, use Redis:
        # 'BACKEND': 'channels_redis.core.RedisChannelLayer',
        # 'CONFIG': {
        #     "hosts": [('127.0.0.1', 6379)],
        # },
    },
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
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'debug.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'api_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'api_requests.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'api.requests': {  # New logger for API requests
            'handlers': ['api_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}


# Add to your settings.py
SITE_NAME = os.getenv('SITE_NAME', 'Auction Platform')  # Default site name
VERIFICATION_TOKEN_EXPIRATION_HOURS = int(os.getenv('VERIFICATION_TOKEN_EXPIRATION_HOURS', 24))  # Token expiration in hours
