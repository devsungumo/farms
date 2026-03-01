from pathlib import Path
from datetime import timedelta
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
    CORS_ALLOWED_ORIGINS=(list, []),
)
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY', default='django-insecure-change-me')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

INSTALLED_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # social providers — add/remove as needed
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.github',
    # dj-rest-auth
    'dj_rest_auth',
    'dj_rest_auth.registration',
    # local
    'apps.core',
    'apps.user',
    'apps.blog',
    'apps.products',
    'apps.inventory',
    'apps.delivery',
    'apps.cart',
    'apps.orders',
    'apps.payments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'farms.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'farms.wsgi.application'

DATABASES = {
    'default': env.db('DATABASE_URL', default=f'sqlite:///{BASE_DIR}/db.sqlite3'),
}

AUTH_USER_MODEL = 'user.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# django-allauth
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

# Social account — OAuth app credentials are configured via Django admin
# (Social Applications). The settings below control provider behaviour.
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
    },
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'FIELDS': ['id', 'email', 'name', 'first_name', 'last_name'],
    },
    'github': {
        'SCOPE': ['user:email'],
    },
}

# Social OAuth callback URLs — must match what's registered in each provider's console
# and what the frontend sends as redirect_uri
GOOGLE_CALLBACK_URL = env('GOOGLE_CALLBACK_URL', default='http://localhost:3000/auth/google/callback')
GITHUB_CALLBACK_URL = env('GITHUB_CALLBACK_URL', default='http://localhost:3000/auth/github/callback')

# dj-rest-auth — issues JWT tokens via simplejwt
REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_COOKIE': None,
    'JWT_AUTH_REFRESH_COOKIE': None,
    'JWT_AUTH_HTTPONLY': False,
    'TOKEN_MODEL': None,          # we use JWT, not DRF token auth
    'USER_DETAILS_SERIALIZER': 'apps.user.serializers.UserSerializer',
}

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'apps.core.pagination.StandardPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
    },
}

# JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])
CORS_ALLOW_CREDENTIALS = True   # required for session cookies (anonymous cart)

# API Docs
SPECTACULAR_SETTINGS = {
    'TITLE': 'Farms API',
    'DESCRIPTION': 'Produce farm e-commerce API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Paystack
PAYSTACK_SECRET_KEY = env('PAYSTACK_SECRET_KEY', default='')
PAYSTACK_PUBLIC_KEY = env('PAYSTACK_PUBLIC_KEY', default='')

# Admin UI
UNFOLD = {
    'SITE_TITLE': 'Farms Admin',
    'SITE_HEADER': 'Farms',
    'SITE_URL': '/',
    'NAVIGATION': [
        {
            'title': 'Catalogue',
            'items': [
                {'title': 'Products', 'link': lambda request: '/admin/products/product/'},
                {'title': 'Categories', 'link': lambda request: '/admin/products/category/'},
                {'title': 'Stock Records', 'link': lambda request: '/admin/inventory/stockrecord/'},
                {'title': 'Stock Movements', 'link': lambda request: '/admin/inventory/stockmovement/'},
            ],
        },
        {
            'title': 'Orders & Payments',
            'items': [
                {'title': 'Orders', 'link': lambda request: '/admin/orders/order/'},
                {'title': 'Payment Records', 'link': lambda request: '/admin/payments/paymentrecord/'},
            ],
        },
        {
            'title': 'Delivery',
            'items': [
                {'title': 'Delivery Zones', 'link': lambda request: '/admin/delivery/deliveryzone/'},
            ],
        },
        {
            'title': 'Content',
            'items': [
                {'title': 'Blog Posts', 'link': lambda request: '/admin/blog/post/'},
                {'title': 'Blog Categories', 'link': lambda request: '/admin/blog/category/'},
                {'title': 'Tags', 'link': lambda request: '/admin/blog/tag/'},
            ],
        },
        {
            'title': 'Users',
            'items': [
                {'title': 'Users', 'link': lambda request: '/admin/user/user/'},
                {'title': 'Carts', 'link': lambda request: '/admin/cart/cart/'},
            ],
        },
    ],
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'apps.payments': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'apps.inventory': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'apps.orders': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
    },
}
