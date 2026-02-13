from pathlib import Path
import environ
import os


# Base directory

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # points to backend/


# Environment variables

env = environ.Env()

# Read the .env file located in the same directory as this settings.py file
environ.Env.read_env(os.path.join(Path(__file__).resolve().parent, '.env'))

SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')
ALLOWED_HOSTS = ['47.130.34.119', 'baithulmal.lk', 'www.baithulmal.lk', 'localhost']


# WebXPay API Configuration

WEBXPAY_URL = env("WEBXPAY_URL")
# WEBXPAY_PUBLIC_KEY = env("WEBXPAY_PUBLIC_KEY")
WEBXPAY_API_USERNAME = env("WEBXPAY_API_USERNAME")
WEBXPAY_API_PASSWORD = env("WEBXPAY_API_PASSWORD")
WEBXPAY_RETURN_URL = env("WEBXPAY_RETURN_URL")
WEBXPAY_MERCHANT_ID = env("WEBXPAY_MERCHANT_ID")
WEBXPAY_SECRET = env("WEBXPAY_SECRET")
WEBXPAY_PRODUCT_ID = "PRD-0000886"


# Installed apps

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'payments',
    'corsheaders'
]


# Middleware

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Allow port 3000 (where your HTML is running)
CORS_ALLOWED_ORIGINS = [
    "http://47.131.0.234",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
ALLOWED_HOSTS = ['47.130.34.119', 'baithulmal.lk', 'www.baithulmal.lk', 'localhost', '127.0.0.1']

CSRF_TRUSTED_ORIGINS = ['https://baithulmal.lk', 'https://www.baithulmal.lk']

# Alternatively, for development only, you can allow all (less secure):
# CORS_ALLOW_ALL_ORIGINS = True

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# URL configuration

ROOT_URLCONF = 'core.urls'


# Templates

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Use os.path.join to make the path compatible with any OS
        'DIRS': [os.path.join(BASE_DIR, 'static')], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI

WSGI_APPLICATION = 'core.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
    }
}


# Language & timezone

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# Media files

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

AUTH_USER_MODEL = 'users.CustomUser'