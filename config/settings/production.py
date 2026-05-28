"""
ChicShop — Settings de PRODUCTION
Sécurité maximale activée
"""
from .base import *

DEBUG = False

# ============================================================
# SÉCURITÉ HTTPS — HSTS, cookies sécurisés, etc.
# ============================================================

# HTTPS obligatoire
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# HSTS — Force HTTPS pour 1 an
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookies sécurisés
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

# X-Frame-Options — Anti-clickjacking
X_FRAME_OPTIONS = 'DENY'

# Content sniffing — navigateurs ne doivent pas deviner le type MIME
SECURE_CONTENT_TYPE_NOSNIFF = True

# XSS filter (ancien navigateurs)
SECURE_BROWSER_XSS_FILTER = True

# Referrer Policy
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Content Security Policy — à compléter selon les ressources utilisées
# Utiliser django-csp pour une gestion fine
CSP_DEFAULT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "fonts.googleapis.com")
CSP_FONT_SRC = ("'self'", "fonts.gstatic.com")
CSP_IMG_SRC = ("'self'", "data:", "blob:")
CSP_SCRIPT_SRC = ("'self'",)
CSP_CONNECT_SRC = ("'self'",)

# CSRF — Origines de confiance explicites
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])

# ============================================================
# REST FRAMEWORK — Activer le Browsable API uniquement si debug
# ============================================================
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
    'rest_framework.renderers.JSONRenderer',
]

# ============================================================
# LOGGING production — plus verbeux pour la surveillance
# ============================================================
LOGGING['loggers']['django']['level'] = 'WARNING'
LOGGING['loggers']['chicshop']['level'] = 'WARNING'


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Fichiers statiques
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Autoriser Render
ALLOWED_HOSTS = ['*']  # Ou spécifiez votre URL Render plus tard


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