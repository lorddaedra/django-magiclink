from __future__ import annotations

from django.conf import settings

# flake8: noqa: E501


LOGIN_SENT_REDIRECT_URL: str = getattr(settings, 'MAGICLINKS_LOGIN_SENT_REDIRECT_URL', 'magiclinks:login_sent')

SIGNUP_LOGIN_REDIRECT_URL: str = getattr(settings, 'MAGICLINKS_SIGNUP_LOGIN_REDIRECT_URL', settings.LOGIN_REDIRECT_URL)

REGISTRATION_SALT: str = getattr(settings, 'MAGICLINKS_REGISTRATION_SALT', 'magiclinks')

CREATE_USER_CALLABLE: str = getattr(settings, 'MAGICLINKS_CREATE_USER_CALLABLE', 'magiclinks.services:create_user')
