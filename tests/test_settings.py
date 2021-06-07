from __future__ import annotations

from importlib import reload

import pytest
from django.core.exceptions import ImproperlyConfigured


def test_login_sent_redirect(settings):
    settings.MAGICLINKS_LOGIN_SENT_REDIRECT_URL = '/sent'
    from magiclinks import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.LOGIN_SENT_REDIRECT_URL == settings.MAGICLINKS_LOGIN_SENT_REDIRECT_URL  # NOQA: E501


def test_signup_login_redirect(settings):
    settings.MAGICLINKS_SIGNUP_LOGIN_REDIRECT_URL = '/loggedin'
    from magiclinks import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.SIGNUP_LOGIN_REDIRECT_URL == settings.MAGICLINKS_SIGNUP_LOGIN_REDIRECT_URL  # NOQA: E501


def test_registration_salt(settings):
    settings.MAGICLINKS_REGISTRATION_SALT = 'magiclinkssalt'
    from magiclinks import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.REGISTRATION_SALT == settings.MAGICLINKS_REGISTRATION_SALT  # NOQA: E501


def test_create_user_callable(settings):
    settings.MAGICLINKS_CREATE_USER_CALLABLE = 'some_package.services:create_user'
    from magiclinks import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.CREATE_USER_CALLABLE == settings.MAGICLINKS_CREATE_USER_CALLABLE  # NOQA: E501


def test_create_user_callable_is_not_set(settings):
    settings.MAGICLINKS_CREATE_USER_CALLABLE = ''
    from magiclinks import settings as mlsettings
    with pytest.raises(ImproperlyConfigured):
        reload(mlsettings)
