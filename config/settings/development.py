"""
ChicShop — Settings de DÉVELOPPEMENT
"""
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# BDD SQLite en dev pour la facilité
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'ATOMIC_REQUESTS': True,
    }
}

# Emails dans la console en dev
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS — Tout autoriser en dev
CORS_ALLOW_ALL_ORIGINS = True

# Désactiver HTTPS en dev
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# DRF — Activer le Browsable API en dev
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',
]

# Throttling plus souple en dev
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '1000/hour',
    'user': '10000/hour',
    'login': '100/min',
    'register': '100/hour',
    'order': '200/hour',
    'password_reset': '100/hour',
}

# Cache mémoire en dev (pas de Redis nécessaire)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Celery — Exécuter les tâches de manière synchrone en dev
CELERY_TASK_ALWAYS_EAGER = True

INSTALLED_APPS += ['django_extensions']
