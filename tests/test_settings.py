from __future__ import annotations

from importlib import reload


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
