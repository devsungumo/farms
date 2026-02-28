from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Print emails to console instead of sending them
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Skip email verification locally so signup is frictionless
ACCOUNT_EMAIL_VERIFICATION = 'none'

# Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True
