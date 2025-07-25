"""
Django settings for back project.
"""
from pathlib import Path
import os
import sys
import random
from datetime import timedelta

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv
from django.utils import timezone

load_dotenv(os.path.join(Path(__file__).resolve().parent.parent.parent, '.env'))

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ENVIRONMENT DETECTION
# ===================
def is_running_in_docker():
    """Check if we're running inside a Docker container"""
    return os.path.exists('/.dockerenv')

# Detect environment
RUNNING_IN_DOCKER = is_running_in_docker()
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# If no explicit environment is set, infer from other indicators
if not os.getenv('ENVIRONMENT'):
    if RUNNING_IN_DOCKER:
        ENVIRONMENT = 'production' if not DEBUG else 'development'
    else:
        ENVIRONMENT = 'development'

print(f"🔥 ENVIRONMENT: {ENVIRONMENT}")
print(f"🔥 DEBUG MODE: {DEBUG}")
print(f"🔥 RUNNING IN DOCKER: {RUNNING_IN_DOCKER}")

# SECURITY
# ========
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'django-insecure-' + ''.join([chr(random.randint(65, 90)) for _ in range(50)])
        print("⚠️  Using auto-generated SECRET_KEY for development")
    else:
        raise ImproperlyConfigured("SECRET_KEY environment variable is missing")

# Company details
COMPANY_NAME = os.getenv('COMPANY_NAME', 'Real Estate Auctions')
print(f"🔥 COMPANY: {COMPANY_NAME}")

# ALLOWED HOSTS
# =============
ALLOWED_HOSTS = []
if os.getenv('ALLOWED_HOSTS'):
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')

# The ALLOWED_HOSTS is primarily configured via the environment variable in docker-compose.
# The block that extended this list with hardcoded values has been removed to avoid conflicts.

# Add Docker container names if running in Docker
if RUNNING_IN_DOCKER:
    ALLOWED_HOSTS.extend(['auction_backend', 'backend'])

print(f"🔥 ALLOWED_HOSTS: {ALLOWED_HOSTS}")

# DATABASE CONFIGURATION
# ======================
def get_database_config():
    """Get database configuration based on environment"""
    
    # Default values for local development
    default_config = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'auction'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
    

def get_database_config():
    """Get database configuration based on environment"""
    
    # Default to SQLite for simplicity and reliability
    sqlite_config = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
    
    # Only use PostgreSQL if explicitly requested
    if os.getenv('USE_POSTGRESQL', 'False').lower() == 'true':
        print(f"🔥 DATABASE: Using PostgreSQL (explicitly requested)")
        postgresql_config = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'auction'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
            'PORT': os.getenv('DB_PORT', '5432'),
            'CONN_MAX_AGE': 60,
            'OPTIONS': {
                'connect_timeout': 10,
            }
        }
        
        # Determine the database host
        if RUNNING_IN_DOCKER:
            postgresql_config['HOST'] = 'db'
            print(f"🔥 DATABASE: PostgreSQL with Docker service 'db'")
        else:
            postgresql_config['HOST'] = 'localhost'
            print(f"🔥 DATABASE: PostgreSQL with localhost")
        
        return postgresql_config
    
    print(f"🔥 DATABASE: Using SQLite (default)")
    return sqlite_config

DATABASES = {'default': get_database_config()}

# REDIS CONFIGURATION
# ===================
def get_redis_url():
    """Get Redis URL based on environment"""
    redis_url = os.getenv('REDIS_URL')
    
    if redis_url:
        print(f"🔥 REDIS: Using explicit REDIS_URL")
        return redis_url
    elif RUNNING_IN_DOCKER:
        redis_url = 'redis://redis:6379/0'
        print(f"🔥 REDIS: Using Docker service name")
        return redis_url
    else:
        redis_url = 'redis://localhost:6379/0'
        print(f"🔥 REDIS: Using localhost for local development")
        return redis_url

REDIS_URL = get_redis_url()

# SSL AND SECURITY SETTINGS
# =========================
if DEBUG or ENVIRONMENT == 'development':
    print("🔥 DEVELOPMENT MODE - Security features relaxed")
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
else:
    print("🔥 PRODUCTION MODE - Security features enabled")
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True').lower() == 'true'
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# CORS CONFIGURATION
# ==================
# We prioritize the environment variable from docker-compose, with a fallback for local dev.
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [origin for origin in os.getenv('CORS_ALLOWED_ORIGINS', '').split(',') if origin]

# if not CORS_ALLOWED_ORIGINS:
if DEBUG or ENVIRONMENT == 'development':
    print("🔥 CORS: Using default development origins")
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:7500", "http://127.0.0.1:7500",
        "http://localhost:5173", "http://127.0.0.1:5173",
        "https://auction.pinealdevelopers.com",
        "http://auction.pinealdevelopers.com",
    ]
else:
    # For production, trust the specific frontend domain.
    # This can be overridden by the CORS_ALLOWED_ORIGINS env var.
    CORS_ALLOWED_ORIGINS = [
        "https://auction.pinealdevelopers.com",
        "http://auction.pinealdevelopers.com"
    ]

print(f"🔥 CORS_ALLOWED_ORIGINS: {CORS_ALLOWED_ORIGINS}")
CSRF_TRUSTED_ORIGINS = [
    "https://auction.pinealdevelopers.com",
    "http://auction.pinealdevelopers.com",
]

# Common CORS settings
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept', 'accept-encoding', 'authorization', 'content-type',
    'dnt', 'origin', 'user-agent', 'x-csrftoken', 'x-requested-with',
]
CORS_ALLOW_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT']

# APPLICATION DEFINITION
# =====================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'channels',
    'django_filters',
    
    # Local apps
    'accounts',
    'base',
]

# Add to MIDDLEWARE in back/back/settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.RequestLogMiddleware',
    'accounts.middleware.LoginTrackingMiddleware',
    'accounts.middleware.SuperuserOnlyAdminMiddleware',  # ✅ NEW: Superuser only admin access
]

ROOT_URLCONF = 'back.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'back.wsgi.application'
ASGI_APPLICATION = 'back.asgi.application'

# PASSWORD VALIDATION
# ==================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# INTERNATIONALIZATION
# ====================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

LANGUAGES = [('en', _('English')), ('ar', _('Arabic'))]

# CUSTOM USER MODEL
# ================
AUTH_USER_MODEL = 'accounts.CustomUser'

# STATIC FILES
# ============
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# MEDIA FILES
# ===========
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST FRAMEWORK
# ==============
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticatedOrReadOnly',),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {'anon': '100/hour', 'user': '1000/hour'},
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%S.%fZ',
    'DATETIME_INPUT_FORMATS': ['%Y-%m-%dT%H:%M:%S.%fZ', 'iso-8601'],
}

# JWT SETTINGS
# ============
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# CHANNEL LAYERS
# ==============
def get_channel_layers_config():
    """Get channel layers configuration based on environment"""
    if ENVIRONMENT == 'development' and not RUNNING_IN_DOCKER:
        # Use in-memory channel layer for local development
        return {
            'default': {
                'BACKEND': 'channels.layers.InMemoryChannelLayer',
            }
        }
    else:
        # Use Redis for production/Docker environments
        return {
            'default': {
                'BACKEND': 'channels_redis.core.RedisChannelLayer',
                'CONFIG': {
                    "hosts": [REDIS_URL],
                    "capacity": 1500,
                    "expiry": 10,
                },
            }
        }

CHANNEL_LAYERS = get_channel_layers_config()

# CACHE CONFIGURATION
# ===================
def get_cache_config():
    """Get cache configuration based on environment"""
    # Default to database cache for SQLite compatibility
    if os.getenv('USE_REDIS_CACHE', 'False').lower() == 'true':
        print("🔥 CACHE: Using Redis cache")
        return {
            'default': {
                'BACKEND': 'django.core.cache.backends.redis.RedisCache',
                'LOCATION': REDIS_URL,
                'KEY_PREFIX': f'auction_{ENVIRONMENT}',
                'TIMEOUT': 300,
            }
        }
    else:
        # Use database cache (SQLite compatible)
        print("🔥 CACHE: Using database cache (SQLite compatible)")
        return {
            'default': {
                'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
                'LOCATION': 'cache_table',
                'TIMEOUT': 300,
                'KEY_PREFIX': f'auction_{ENVIRONMENT}',
            }
        }

CACHES = get_cache_config()

# Create cache table for database cache (will be ignored if not using db cache)
# Note: You'll need to run 'python manage.py createcachetable' for this to work

# SESSION CONFIGURATION
# ====================
def get_session_config():
    """Get session configuration based on environment"""
    # Default to database sessions for SQLite compatibility
    if os.getenv('USE_CACHE_SESSIONS', 'False').lower() == 'true':
        print("🔥 SESSION: Using cache sessions")
        return 'django.contrib.sessions.backends.cache'
    else:
        # Use database sessions (SQLite compatible)
        print("🔥 SESSION: Using database sessions (SQLite compatible)")
        return 'django.contrib.sessions.backends.db'

SESSION_ENGINE = get_session_config()
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400 * 7  # 7 days
SESSION_COOKIE_NAME = 'auction_sessionid'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# EMAIL CONFIGURATION
# ==================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Use console backend for local development if requested
if DEBUG and os.getenv('USE_CONSOLE_EMAIL', 'False').lower() == 'true':
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    print("🔥 EMAIL: Using console backend")
else:
    print("🔥 EMAIL: Using SMTP backend")

EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
SERVER_EMAIL = DEFAULT_FROM_EMAIL

if not EMAIL_HOST_USER and not DEBUG:
    print("⚠️  WARNING: EMAIL_HOST_USER not set")
if not EMAIL_HOST_PASSWORD and not DEBUG:
    print("⚠️  WARNING: EMAIL_HOST_PASSWORD not set")

print(f"🔥 EMAIL CONFIG: Host={EMAIL_HOST}, Port={EMAIL_PORT}, User={EMAIL_HOST_USER}, TLS={EMAIL_USE_TLS}")

# FRONTEND URL
# ===========
FRONTEND_URL = os.getenv('FRONTEND_URL')
if not FRONTEND_URL:
    if DEBUG or ENVIRONMENT == 'development':
        FRONTEND_URL = 'http://localhost:7500'
    else:
        FRONTEND_URL = 'https://auction.pinealdevelopers.com'

# SITE CONFIGURATION
# ==================
SITE_NAME = COMPANY_NAME
VERIFICATION_TOKEN_EXPIRATION_HOURS = int(os.getenv('VERIFICATION_TOKEN_EXPIRATION_HOURS', 24))

# FILE UPLOAD SETTINGS
# ====================
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_PERMISSIONS = 0o644

# LOGGING CONFIGURATION
# ====================
LOGGING_EXCLUDED_PATHS = [
    r'^/admin/', r'^/static/', r'^/media/', r'^/favicon\.ico$',
    r'^/test/', r'^/debug/',
]

LOGIN_PATH_REGEX = r'/api/accounts/login/?$'
SLOW_REQUEST_THRESHOLD_MS = 1000
LOGIN_SECURITY_ALERTS = not DEBUG

# Create logs directory
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'console': {
            'format': '🔥 {levelname} {asctime} {module} - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console' if DEBUG else 'simple',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'django.log'),
            'formatter': 'verbose',
        },
        'error_file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'error.log'),
            'formatter': 'verbose',
            'level': 'ERROR',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'] + (['file'] if not DEBUG else []),
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'accounts': {
            'handlers': ['console'] + (['file'] if not DEBUG else []),
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'base': {
            'handlers': ['console'] + (['file'] if not DEBUG else []),
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

print(f"🔥 SETTINGS LOADED - DEBUG: {DEBUG}")
print(f"🔥 SETTINGS LOADED - ENVIRONMENT: {ENVIRONMENT}")
print(f"🔥 SETTINGS LOADED - CACHE_BACKEND: {CACHES['default']['BACKEND']}")
print(f"🔥 SETTINGS LOADED - SESSION_ENGINE: {SESSION_ENGINE}")