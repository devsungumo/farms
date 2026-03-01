from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Print emails to console instead of sending them
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Skip email verification locally so signup is frictionless
ACCOUNT_EMAIL_VERIFICATION = 'none'

# Specific origins so CORS_ALLOW_CREDENTIALS can work (wildcard + credentials is
# rejected by browsers). The Vite proxy makes /api same-origin, so these mainly
# cover direct API access (curl, Swagger UI hitting a separate Django dev server).
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]
CORS_ALLOW_CREDENTIALS = True
