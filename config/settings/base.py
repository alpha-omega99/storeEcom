"""
ChicShop — Configuration Django de base
Sécurisée, modulaire, prête pour la production
"""
import os
from pathlib import Path
from datetime import timedelta
import environ
import dj_database_url

# ============================================================
# CHEMINS
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Chargement des variables d'environnement
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / '.env')

# ============================================================
# SÉCURITÉ — Clé secrète (jamais en dur !)
# ============================================================
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# ============================================================
# APPLICATIONS
# ============================================================
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
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.products',
    'apps.orders',
    'apps.payments',
    'apps.shop',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ============================================================
# MIDDLEWARES — Ordre critique pour la sécurité
# ============================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',       # Static files
    'corsheaders.middleware.CorsMiddleware',             # CORS avant CommonMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',         # Protection CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Anti-clickjacking
    'apps.accounts.middleware.SecurityHeadersMiddleware', # Headers custom
    'apps.accounts.middleware.RequestLoggingMiddleware',  # Audit log
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.shop.context_processors.shop_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ============================================================
# BASE DE DONNÉES — Support DATABASE_URL (Render/Heroku) ou variables séparées (local)
# ============================================================
DATABASE_URL = env('DATABASE_URL', default=None)

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    # Fallback pour collectstatic et autres commandes sans DB
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(BASE_DIR / 'db.sqlite3'),
        }
    }

# Sécurité : transactions atomiques par requête HTTP
if DATABASES and 'default' in DATABASES:
    DATABASES['default']['ATOMIC_REQUESTS'] = True
# ============================================================
# AUTHENTIFICATION PERSONNALISÉE
# ============================================================
AUTH_USER_MODEL = 'accounts.User'

# Validation des mots de passe — robuste
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    'OPTIONS': {'min_length': 10}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    {'NAME': 'apps.accounts.validators.PasswordStrengthValidator'},
]

# Hachage : Argon2 > bcrypt > PBKDF2 (recommandation OWASP)
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

# ============================================================
# DJANGO REST FRAMEWORK
# ============================================================
REST_FRAMEWORK = {
    # Authentification JWT par défaut
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    # Refuser l'accès par défaut — explicitement ouvrir les endpoints publics
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # Pagination sécurisée (évite les dumps complets de données)
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'MAX_PAGE_SIZE': 100,
    # Throttling — protection anti-brute-force et DDoS
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'login': '5/min',        # Critique : anti brute-force
        'register': '10/hour',
        'order': '20/hour',
        'password_reset': '3/hour',
    },
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    # Schéma OpenAPI pour la doc
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    # Messages d'erreur uniformes
    'EXCEPTION_HANDLER': 'apps.accounts.exceptions.custom_exception_handler',
    # Désactiver le Browsable API en prod (surface d'attaque)
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
}

# ============================================================
# JWT — Tokens sécurisés
# ============================================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),     # Court pour limiter l'exposition
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,                       # Nouveau refresh à chaque usage
    'BLACKLIST_AFTER_ROTATION': True,                    # Invalider l'ancien
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'TOKEN_OBTAIN_SERIALIZER': 'apps.accounts.serializers.CustomTokenObtainSerializer',
}

# ============================================================
# CACHE — Redis (sessions, rate limiting, données fréquentes)
# ============================================================
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://127.0.0.1:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'CONNECTION_POOL_KWARGS': {'max_connections': 50},
        },
        'KEY_PREFIX': 'chicshop',
        'TIMEOUT': 300,  # 5 min par défaut
    }
}

# Sessions stockées en Redis (pas dans les cookies/DB)
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 3600  # 1 heure
SESSION_COOKIE_HTTPONLY = True   # Inaccessible au JS
SESSION_COOKIE_SAMESITE = 'Lax'

# ============================================================
# CELERY — Tâches asynchrones (emails, WhatsApp, etc.)
# ============================================================
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/1')
CELERY_RESULT_BACKEND = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Abidjan'
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_MAX_RETRIES = 3

# ============================================================
# EMAIL
# ============================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='localhost')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='ChicShop <noreply@chicshop.ci>')

# ============================================================
# FICHIERS
# ============================================================
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Abidjan'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
_static_dir = BASE_DIR / 'static'
STATICFILES_DIRS = [_static_dir] if _static_dir.exists() else []

MEDIA_URL = '/media/'
MEDIA_ROOT = env('MEDIA_ROOT', default=str(BASE_DIR / 'media'))

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================
# CORS — Contrôle strict des origines
# ============================================================
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
    'http://localhost:3000',
    'http://127.0.0.1:3000',
])
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT']
CORS_ALLOW_HEADERS = [
    'accept', 'accept-encoding', 'authorization',
    'content-type', 'dnt', 'origin', 'user-agent',
    'x-csrftoken', 'x-requested-with',
]

# ============================================================
# DOCUMENTATION API — DRF Spectacular
# ============================================================
SPECTACULAR_SETTINGS = {
    'TITLE': 'ChicShop API',
    'DESCRIPTION': 'API REST pour la boutique ChicShop — Tapis de prière personnalisés',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}

# ============================================================
# WHATSAPP BUSINESS API
# ============================================================
WHATSAPP_API_TOKEN = env('WHATSAPP_API_TOKEN', default='')
WHATSAPP_PHONE_NUMBER_ID = env('WHATSAPP_PHONE_NUMBER_ID', default='')
WHATSAPP_ADMIN_NUMBER = env('WHATSAPP_ADMIN_NUMBER', default='')

# ============================================================
# VALIDATION TÉLÉPHONE (Côte d'Ivoire)
# ============================================================
PHONENUMBER_DEFAULT_REGION = 'CI'

# ============================================================
# LOGGING — Audit et surveillance
# ============================================================
# BASE_DIR est déjà un objet Path (ex: C:\Projet\chicshop_backend)
# On crée un dossier 'logs' à la racine du projet s'il n'existe pas
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE_NAME = env('LOG_FILE', default='django.log')
LOG_FILE_PATH = str(LOG_DIR / LOG_FILE_NAME)
SECURITY_LOG_NAME = env('SECURITY_LOG_FILE', default='security.log')
SECURITY_LOG_PATH = str(LOG_DIR / SECURITY_LOG_NAME)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'security': {
            'format': '[{asctime}] SECURITY {levelname} IP={request_ip} USER={user} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILE_PATH,  # <--- Utilise la variable universelle
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'security_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': SECURITY_LOG_PATH, # <--- Utilise la variable universelle
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': env('LOG_LEVEL', default='WARNING'),
        },
        'django.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'chicshop.security': {
            'handlers': ['security_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'chicshop': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
    },
}

# ============================================================
# PARAMÈTRES MÉTIER CHICSHOP
# ============================================================
CHICSHOP = {
    'CURRENCY': 'XOF',          # Franc CFA
    'CURRENCY_SYMBOL': 'F CFA',
    'MIN_ORDER_AMOUNT': 1000,    # 1 000 F CFA minimum
    'MAX_CART_ITEMS': 20,
    'MAX_EMBROIDERY_LENGTH': 20, # Caractères max pour le prénom brodé
    'ORDER_REF_PREFIX': 'CS',
    'PROMO_CODE_ACTIVE': 'CHICSHOP15',
    'PROMO_CODE_DISCOUNT': 15,   # %
    'FREE_DELIVERY_MIN': 0,      # Livraison toujours gratuite
    'WHATSAPP_RESPONSE_TIME_MIN': 5,
}
