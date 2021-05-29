from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

# flake8: noqa: E501


LOGIN_SENT_REDIRECT = getattr(settings, 'MAGICLINK_LOGIN_SENT_REDIRECT', 'magiclink:login_sent')

SIGNUP_LOGIN_REDIRECT = getattr(settings, 'MAGICLINK_SIGNUP_LOGIN_REDIRECT', '')

try:
    # In seconds
    AUTH_TIMEOUT = int(getattr(settings, 'MAGICLINK_AUTH_TIMEOUT', 300))
except ValueError:
    raise ImproperlyConfigured('"MAGICLINK_AUTH_TIMEOUT" must be an integer')

try:
    # In seconds
    LOGIN_REQUEST_TIME_LIMIT = int(getattr(settings, 'MAGICLINK_LOGIN_REQUEST_TIME_LIMIT', 30))
except ValueError:
    raise ImproperlyConfigured('"MAGICLINK_LOGIN_REQUEST_TIME_LIMIT" must be an integer')


ANTISPAM_FORMS = getattr(settings, 'MAGICLINK_ANTISPAM_FORMS', False)
if not isinstance(ANTISPAM_FORMS, bool):
    raise ImproperlyConfigured('"MAGICLINK_ANTISPAM_FORMS" must be a boolean')
ANTISPAM_FIELD_TIME = getattr(settings, 'MAGICLINK_ANTISPAM_FIELD_TIME', 1)
if ANTISPAM_FIELD_TIME is not None:
    try:
        ANTISPAM_FIELD_TIME = float(ANTISPAM_FIELD_TIME)
    except ValueError:
        raise ImproperlyConfigured('"MAGICLINK_ANTISPAM_FIELD_TIME" must be a float')
