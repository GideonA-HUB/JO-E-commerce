"""
Railway-specific settings for TASTY FINGERS
Optimized for Railway deployment without 301 redirects
"""
import os
from .settings import *

# Override settings for Railway deployment
DEBUG = False

# Railway-specific settings
ALLOWED_HOSTS = [
    'tasty-fingers.up.railway.app',
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    '.railway.app',  # Allow all railway.app subdomains
]

# Disable SSL redirect for Railway (Railway handles HTTPS)
SECURE_SSL_REDIRECT = False
SECURE_REDIRECT_EXEMPT = [
    r'^/api/.*$',
    r'^/admin/.*$',
    r'^/static/.*$',
    r'^/media/.*$',
    r'^/$',
    r'^/track-order/.*$',
]

# CORS settings for Railway
CORS_ALLOWED_ORIGINS = [
    'https://tasty-fingers.up.railway.app',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

# Disable CORS for all origins in production
CORS_ALLOW_ALL_ORIGINS = False

# Security settings (Railway handles HTTPS)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_PRELOAD = True

# Cookie settings (Railway provides HTTPS)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Additional security headers
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'

# Static files configuration for Railway
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Use WhiteNoise for static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Logging for Railway
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
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Email settings for Railway
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'gideonamienz24@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'bfdq jmxo ppuo izkt')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'gideonamienz24@gmail.com')

# Site settings
SITE_NAME = 'TASTY FINGERS'
SITE_URL = 'https://tasty-fingers.up.railway.app'
ADMIN_EMAIL = 'gideonamienz24@gmail.com'

# Cloudinary settings
CLOUDINARY = {
    'cloud_name': 'dao40lt42',
    'api_key': '138773767419866',
    'api_secret': 'Q-099CT3pgd-uHAt60xVDVRg-ok',
}

# Paystack settings
PAYSTACK_PUBLIC_KEY = os.environ.get('PAYSTACK_PUBLIC_KEY', 'pk_test_your_paystack_public_key_here')
PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY', 'sk_test_your_paystack_secret_key_here')
PAYSTACK_WEBHOOK_SECRET = os.environ.get('PAYSTACK_WEBHOOK_SECRET', 'whsec_your_paystack_webhook_secret_here')

print("🚀 Railway settings loaded successfully!")
print(f"DEBUG: {DEBUG}")
print(f"SECURE_SSL_REDIRECT: {SECURE_SSL_REDIRECT}")
print(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(f"CORS_ALLOWED_ORIGINS: {CORS_ALLOWED_ORIGINS}")
