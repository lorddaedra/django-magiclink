from __future__ import annotations

from importlib import reload


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
