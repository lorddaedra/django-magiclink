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
