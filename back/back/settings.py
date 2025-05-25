from pathlib import Path
import os, sys
from datetime import timedelta
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(env_path)

BASE_DIR = Path(__file__).resolve().parent.parent

def get_env_variable(var_name, default=None, required=False):
    """Get environment variable with error handling"""
    value = os.getenv(var_name, default)
    if required and not value:
        raise ImproperlyConfigured(f"{var_name} environment variable is required")
    return value

def get_bool_env(var_name, default='False'):
    """Convert environment variable to boolean"""
    return get_env_variable(var_name, default).lower() in ('true', '1', 'yes', 'on')

def get_list_env(var_name, default='', separator=','):
    """Convert environment variable to list"""
    value = get_env_variable(var_name, default)
    return [item.strip() for item in value.split(separator) if item.strip()]

# Core Settings
SECRET_KEY = get_env_variable('SECRET_KEY', required=True)
DEBUG = get_bool_env('DEBUG', 'True')
ALLOWED_HOSTS = get_list_env('ALLOWED_HOSTS', 'localhost,127.0.0.1')

# Company Configuration
COMPANY_NAME = get_env_variable('COMPANY_NAME', 'Auctions')
FRONTEND_URL = get_env_variable('FRONTEND_URL', 'http://localhost:5137').rstrip('/')

# Application Definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'channels',
    'django_filters',
]

LOCAL_APPS = [
    'accounts',
    'base',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Temporarily commented out to fix admin issue
    # 'accounts.middleware.RequestLogMiddleware',
    # 'accounts.middleware.LoginTrackingMiddleware',
]

ROOT_URLCONF = 'back.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'back.wsgi.application'
ASGI_APPLICATION = 'back.asgi.application'

# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,
        }
    }
}

# PostgreSQL Configuration (for production deployment)
# Uncomment and configure for production:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': get_env_variable('DB_NAME', 'auction_db'),
#         'USER': get_env_variable('DB_USER', 'auction_user'),
#         'PASSWORD': get_env_variable('DB_PASSWORD', required=True),
#         'HOST': get_env_variable('DB_HOST', 'localhost'),
#         'PORT': get_env_variable('DB_PORT', '5432'),
#         'OPTIONS': {
#             'connect_timeout': 10,
#             'options': '-c default_transaction_isolation=read_committed'
#         },
#         'CONN_MAX_AGE': 60,
#     }
# }

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# Redis Cache Configuration (for production)
# Uncomment for production with Redis:
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': get_env_variable('REDIS_URL', 'redis://127.0.0.1:6379/1'),
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#             'CONNECTION_POOL_KWARGS': {'max_connections': 20},
#             'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
#         },
#         'TIMEOUT': 300
#     }
# }

# Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = get_env_variable('TIME_ZONE', 'UTC')
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('en', _('English')),
    ('ar', _('Arabic')),
]

LOCALE_PATHS = [BASE_DIR / 'locale']

# Custom User Model
AUTH_USER_MODEL = 'accounts.CustomUser'

# Static Files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Media Files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_PERMISSIONS = 0o644

# Default Primary Key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ] + (['rest_framework.renderers.BrowsableAPIRenderer'] if DEBUG else []),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/day' if DEBUG else '100/day',
        'user': '10000/day' if DEBUG else '1000/day',
        'login': '5/min',
        'register': '3/min',
    },
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# WebSocket Configuration
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer' if DEBUG else 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {} if DEBUG else {
            'hosts': [(get_env_variable('REDIS_HOST', '127.0.0.1'), int(get_env_variable('REDIS_PORT', '6379')))],
            'capacity': 1500,
            'expiry': 10,
        },
    }
}

# Redis Configuration for Production WebSockets
# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {
#             'hosts': [get_env_variable('REDIS_URL', 'redis://localhost:6379/0')],
#             'capacity': 1500,
#             'expiry': 10,
#             'symmetric_encryption_keys': [SECRET_KEY],
#         },
#     },
# }

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = get_list_env('CORS_ALLOWED_ORIGINS', FRONTEND_URL) if not DEBUG else []
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept', 'accept-encoding', 'authorization', 'content-type',
    'dnt', 'origin', 'user-agent', 'x-csrftoken', 'x-requested-with',
    'cache-control', 'pragma', 'if-modified-since',
]

# Email Configuration
EMAIL_BACKEND = get_env_variable('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = get_env_variable('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(get_env_variable('EMAIL_PORT', '587'))
EMAIL_USE_TLS = get_bool_env('EMAIL_USE_TLS', 'True')
EMAIL_USE_SSL = get_bool_env('EMAIL_USE_SSL', 'False')
EMAIL_HOST_USER = get_env_variable('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_env_variable('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = get_env_variable('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or f'noreply@{COMPANY_NAME.lower().replace(" ", "")}.com')
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Email Template Paths
EMAIL_VERIFY_PATH = get_env_variable('EMAIL_VERIFY_PATH', '/verify-email')
PASSWORD_RESET_PATH = get_env_variable('PASSWORD_RESET_PATH', '/reset-password')

# Security Settings
if not DEBUG:
    # HTTPS Settings
    SECURE_SSL_REDIRECT = get_bool_env('SECURE_SSL_REDIRECT', 'True')
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Cookie Security
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SAMESITE = 'Lax'
    
    # Security Headers
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_REFERRER_POLICY = 'same-origin'
    
    # Additional Security
    X_FRAME_OPTIONS = 'DENY'
    SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 1209600  # 2 weeks

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {module} {funcName}:{lineno} - {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {name} - {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': ['require_debug_true'],
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.expanduser('~/auction_django.log'),
            'maxBytes': 1024*1024*5,  # 5MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.expanduser('~/auction_error.log'),
            'maxBytes': 1024*1024*5,  # 5MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['error_file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'accounts': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'base': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# Create logs directory
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Rate Limiting Configuration
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# Custom Settings
VERIFICATION_TOKEN_EXPIRATION_HOURS = int(get_env_variable('VERIFICATION_TOKEN_EXPIRATION_HOURS', '24'))
LOGIN_SECURITY_ALERTS = get_bool_env('LOGIN_SECURITY_ALERTS', 'False')
SLOW_REQUEST_THRESHOLD_MS = int(get_env_variable('SLOW_REQUEST_THRESHOLD_MS', '1000'))

# Admin Configuration
ADMIN_URL = get_env_variable('ADMIN_URL', 'admin/')
ADMINS = [
    ('Admin', get_env_variable('ADMIN_EMAIL', 'admin@example.com')),
]
MANAGERS = ADMINS

# Pagination Settings
REST_FRAMEWORK_PAGINATION = {
    'DEFAULT_LIMIT': 20,
    'LIMIT_QUERY_PARAM': 'limit',
    'OFFSET_QUERY_PARAM': 'offset',
    'MAX_LIMIT': 100
}

# Performance Settings
if not DEBUG:
    # Database connection pooling
    DATABASES['default']['CONN_MAX_AGE'] = 60
    
    # Template caching
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]

# Environment-specific configurations
ENVIRONMENT = get_env_variable('ENVIRONMENT', 'development')

if ENVIRONMENT == 'production':
    # Production-specific settings
    ALLOWED_HOSTS = get_list_env('ALLOWED_HOSTS', required=True)
    
    # Use whitenoise for static files in production
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'