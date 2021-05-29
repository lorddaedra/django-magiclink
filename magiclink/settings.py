from __future__ import annotations

from django.conf import settings

# flake8: noqa: E501


LOGIN_SENT_REDIRECT = getattr(settings, 'MAGICLINK_LOGIN_SENT_REDIRECT', 'magiclink:login_sent')

SIGNUP_LOGIN_REDIRECT = getattr(settings, 'MAGICLINK_SIGNUP_LOGIN_REDIRECT', '')
