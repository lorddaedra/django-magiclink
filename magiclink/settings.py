from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

# flake8: noqa: E501


LOGIN_SENT_REDIRECT = getattr(settings, 'MAGICLINK_LOGIN_SENT_REDIRECT', 'magiclink:login_sent')

SIGNUP_LOGIN_REDIRECT = getattr(settings, 'MAGICLINK_SIGNUP_LOGIN_REDIRECT', '')

ANTISPAM_FORMS = getattr(settings, 'MAGICLINK_ANTISPAM_FORMS', False)
if not isinstance(ANTISPAM_FORMS, bool):
    raise ImproperlyConfigured('"MAGICLINK_ANTISPAM_FORMS" must be a boolean')
ANTISPAM_FIELD_TIME = getattr(settings, 'MAGICLINK_ANTISPAM_FIELD_TIME', 1)
if ANTISPAM_FIELD_TIME is not None:
    try:
        ANTISPAM_FIELD_TIME = float(ANTISPAM_FIELD_TIME)
    except ValueError:
        raise ImproperlyConfigured('"MAGICLINK_ANTISPAM_FIELD_TIME" must be a float')
