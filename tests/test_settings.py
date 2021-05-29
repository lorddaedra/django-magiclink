from __future__ import annotations

from importlib import reload

import pytest
from django.core.exceptions import ImproperlyConfigured


def test_login_sent_redirect(settings):
    settings.MAGICLINK_LOGIN_SENT_REDIRECT = '/sent'
    from magiclink import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.LOGIN_SENT_REDIRECT == settings.MAGICLINK_LOGIN_SENT_REDIRECT  # NOQA: E501


def test_signup_login_redirect(settings):
    settings.MAGICLINK_SIGNUP_LOGIN_REDIRECT = '/loggedin'
    from magiclink import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.SIGNUP_LOGIN_REDIRECT == settings.MAGICLINK_SIGNUP_LOGIN_REDIRECT  # NOQA: E501


def test_email_subject(settings):
    settings.MAGICLINK_EMAIL_SUBJECT = 'Test Email subject'
    from magiclink import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.EMAIL_SUBJECT == settings.MAGICLINK_EMAIL_SUBJECT


def test_email_template_name_text(settings):
    settings.MAGICLINK_EMAIL_TEMPLATE_NAME_TEXT = 'email.txt'
    from magiclink import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.EMAIL_TEMPLATE_NAME_TEXT == settings.MAGICLINK_EMAIL_TEMPLATE_NAME_TEXT  # NOQA: E501


def test_email_template_name_html(settings):
    settings.MAGICLINK_EMAIL_TEMPLATE_NAME_HTML = 'email.html'
    from magiclink import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.EMAIL_TEMPLATE_NAME_HTML == settings.MAGICLINK_EMAIL_TEMPLATE_NAME_HTML  # NOQA: E501


def test_token_length(settings):
    settings.MAGICLINK_TOKEN_LENGTH = 100
    from magiclink import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.TOKEN_LENGTH == settings.MAGICLINK_TOKEN_LENGTH


def test_token_length_bad_value(settings):
    settings.MAGICLINK_TOKEN_LENGTH = 'Test'

    with pytest.raises(ImproperlyConfigured):
        from magiclink import settings
        reload(settings)


def test_token_length_low_value_warning(settings):
    settings.MAGICLINK_TOKEN_LENGTH = 1

    with pytest.warns(RuntimeWarning):
        from magiclink import settings
        reload(settings)


def test_auth_timeout(settings):
    settings.MAGICLINK_AUTH_TIMEOUT = 100
    from magiclink import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.AUTH_TIMEOUT == settings.MAGICLINK_AUTH_TIMEOUT


def test_auth_timeout_bad_value(settings):
    settings.MAGICLINK_AUTH_TIMEOUT = 'Test'

    with pytest.raises(ImproperlyConfigured):
        from magiclink import settings
        reload(settings)


def test_token_uses(settings):
    settings.MAGICLINK_TOKEN_USES = 100
    from magiclink import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.TOKEN_USES == settings.MAGICLINK_TOKEN_USES


def test_token_uses_bad_value(settings):
    settings.MAGICLINK_TOKEN_USES = 'Test'

    with pytest.raises(ImproperlyConfigured):
        from magiclink import settings
        reload(settings)


def test_token_request_time_limit(settings):
    settings.MAGICLINK_LOGIN_REQUEST_TIME_LIMIT = True
    from magiclink import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.LOGIN_REQUEST_TIME_LIMIT == settings.MAGICLINK_LOGIN_REQUEST_TIME_LIMIT  # NOQA: E501


def test_token_request_time_limit_bad_value(settings):
    settings.MAGICLINK_LOGIN_REQUEST_TIME_LIMIT = 'Test'

    with pytest.raises(ImproperlyConfigured):
        from magiclink import settings
        reload(settings)


def test_antispam_forms(settings):
    settings.MAGICLINK_ANTISPAM_FORMS = True
    from magiclink import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.ANTISPAM_FORMS == settings.MAGICLINK_ANTISPAM_FORMS


def test_antispam_forms_bad_value(settings):
    settings.MAGICLINK_ANTISPAM_FORMS = 'Test'

    with pytest.raises(ImproperlyConfigured):
        from magiclink import settings
        reload(settings)


def test_antispam_form_submit_time(settings):
    settings.MAGICLINK_ANTISPAM_FIELD_TIME = 5
    from magiclink import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.ANTISPAM_FIELD_TIME == settings.MAGICLINK_ANTISPAM_FIELD_TIME  # NOQA: E501


def test_antispam_form_submit_time_bad_value(settings):
    settings.MAGICLINK_ANTISPAM_FIELD_TIME = 'Test'

    with pytest.raises(ImproperlyConfigured):
        from magiclink import settings
        reload(settings)
