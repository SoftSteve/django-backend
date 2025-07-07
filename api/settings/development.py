from .base import *

DEBUG = True

# WARNING: keep this secret key only for local dev
SECRET_KEY = 'django-insecure-!n_^-m+&m3dt2yv=y7%pr$g+$)!nnp@e*as^+2(4x4gpxolpp+'

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '10.0.0.135']

# CORS for React dev server (change IP if needed)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://10.0.0.135:3000",
]

CSRF_TRUSTED_ORIGINS = [
    "http://10.0.0.135:3000",
]

# Database - SQLite (default)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Cookies not secure in dev
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
