# flake8: noqa: E501
import warnings

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

LOGIN_SENT_REDIRECT = getattr(settings, 'MAGICLINK_LOGIN_SENT_REDIRECT', 'magiclink:login_sent')

SIGNUP_LOGIN_REDIRECT = getattr(settings, 'MAGICLINK_SIGNUP_LOGIN_REDIRECT', '')

try:
    TOKEN_LENGTH = int(getattr(settings, 'MAGICLINK_TOKEN_LENGTH', 50))
except ValueError:
    raise ImproperlyConfigured('"MAGICLINK_TOKEN_LENGTH" must be an integer')
else:
    if TOKEN_LENGTH < 20:
        warning = ('Shorter MAGICLINK_TOKEN_LENGTH values make your login more'
                   'sussptable to brute force attacks')
        warnings.warn(warning, RuntimeWarning)

try:
    # In seconds
    AUTH_TIMEOUT = int(getattr(settings, 'MAGICLINK_AUTH_TIMEOUT', 300))
except ValueError:
    raise ImproperlyConfigured('"MAGICLINK_AUTH_TIMEOUT" must be an integer')

try:
    TOKEN_USES = int(getattr(settings, 'MAGICLINK_TOKEN_USES', 1))
except ValueError:
    raise ImproperlyConfigured('"MAGICLINK_TOKEN_USES" must be an integer')

EMAIL_IGNORE_CASE = getattr(settings, 'MAGICLINK_EMAIL_IGNORE_CASE', True)
if not isinstance(EMAIL_IGNORE_CASE, bool):
    raise ImproperlyConfigured('"MAGICLINK_EMAIL_IGNORE_CASE" must be a boolean')

EMAIL_AS_USERNAME = getattr(settings, 'MAGICLINK_EMAIL_AS_USERNAME', True)
if not isinstance(EMAIL_AS_USERNAME, bool):
    raise ImproperlyConfigured('"MAGICLINK_EMAIL_AS_USERNAME" must be a boolean')

IGNORE_IS_ACTIVE_FLAG = getattr(settings, 'MAGICLINK_IGNORE_IS_ACTIVE_FLAG', False)
if not isinstance(IGNORE_IS_ACTIVE_FLAG, bool):
    raise ImproperlyConfigured('"MAGICLINK_IGNORE_IS_ACTIVE_FLAG" must be a boolean')

VERIFY_INCLUDE_EMAIL = getattr(settings, 'MAGICLINK_VERIFY_INCLUDE_EMAIL', True)
if not isinstance(VERIFY_INCLUDE_EMAIL, bool):
    raise ImproperlyConfigured('"MAGICLINK_VERIFY_INCLUDE_EMAIL" must be a boolean')

try:
    # In seconds
    LOGIN_REQUEST_TIME_LIMIT = int(getattr(settings, 'MAGICLINK_LOGIN_REQUEST_TIME_LIMIT', 30))
except ValueError:
    raise ImproperlyConfigured('"MAGICLINK_LOGIN_REQUEST_TIME_LIMIT" must be an integer')


EMAIL_SUBJECT = getattr(settings, 'MAGICLINK_EMAIL_SUBJECT', 'Your login magic link')
EMAIL_TEMPLATE_NAME_TEXT = getattr(settings, 'MAGICLINK_EMAIL_TEMPLATE_NAME_TEXT', 'magiclink/login_email.txt')
EMAIL_TEMPLATE_NAME_HTML = getattr(settings, 'MAGICLINK_EMAIL_TEMPLATE_NAME_HTML', 'magiclink/login_email.html')


ANTISPAM_FORMS = getattr(settings, 'MAGICLINK_ANTISPAM_FORMS', False)
if not isinstance(ANTISPAM_FORMS, bool):
    raise ImproperlyConfigured('"MAGICLINK_ANTISPAM_FORMS" must be a boolean')
ANTISPAM_FIELD_TIME = getattr(settings, 'MAGICLINK_ANTISPAM_FIELD_TIME', 1)
if ANTISPAM_FIELD_TIME is not None:
    try:
        ANTISPAM_FIELD_TIME = float(ANTISPAM_FIELD_TIME)
    except ValueError:
        raise ImproperlyConfigured('"MAGICLINK_ANTISPAM_FIELD_TIME" must be a float')
