from __future__ import annotations

from django.conf import settings

# flake8: noqa: E501


LOGIN_SENT_REDIRECT_URL = getattr(settings, 'MAGICLINKS_LOGIN_SENT_REDIRECT_URL', 'magiclinks:login_sent')

SIGNUP_LOGIN_REDIRECT_URL = getattr(settings, 'MAGICLINKS_SIGNUP_LOGIN_REDIRECT_URL', settings.LOGIN_REDIRECT_URL)

REGISTRATION_SALT = getattr(settings, 'MAGICLINKS_REGISTRATION_SALT', 'magiclinks')
