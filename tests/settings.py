from __future__ import annotations

import os

SECRET_KEY = 'magiclinks-test'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ALLOWED_HOSTS = '*'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

ROOT_URLCONF = 'tests.urls'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tests',
    'magiclinks.apps.MagicLinksConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

AUTHENTICATION_BACKENDS = [
    'magiclinks.backends.MagicLinksBackend',
    'django.contrib.auth.backends.ModelBackend',
]


def create_user(*, email: str):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(username=email, email=email)


AUTH_USER_MODEL = 'tests.User'
LOGIN_URL = 'magiclinks:login'
LOGIN_REDIRECT_URL = 'needs_login'
LOGOUT_REDIRECT_URL = 'no_login'
MAGICLINKS_LOGIN_SENT_REDIRECT_URL = 'magiclinks:login_sent'
MAGICLINKS_SIGNUP_LOGIN_REDIRECT_URL = 'no_login'
MAGICLINKS_REGISTRATION_SALT = 'magiclinks'
MAGICLINKS_CREATE_USER_CALLABLE = 'tests.settings:create_user'
