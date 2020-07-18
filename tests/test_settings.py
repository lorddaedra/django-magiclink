from importlib import reload

import pytest
from django.core.exceptions import ImproperlyConfigured


def test_login_sent_redirect(settings):
    settings.MAGICLINK_LOGIN_SENT_REDIRECT = '/sent'
    from magiclink import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.LOGIN_SENT_REDIRECT == settings.MAGICLINK_LOGIN_SENT_REDIRECT  # NOQA: E501


def test_login_template_name(settings):
    settings.MAGICLINK_LOGIN_TEMPLATE_NAME = 'login.html'
    from magiclink import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.LOGIN_TEMPLATE_NAME == settings.MAGICLINK_LOGIN_TEMPLATE_NAME  # NOQA: E501


def test_login_sent_template_name(settings):
    settings.MAGICLINK_LOGIN_SENT_TEMPLATE_NAME = 'login_sent.html'
    from magiclink import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.LOGIN_SENT_TEMPLATE_NAME == settings.MAGICLINK_LOGIN_SENT_TEMPLATE_NAME  # NOQA: E501


def test_signup_template_name(settings):
    settings.MAGICLINK_SIGNUP_TEMPLATE_NAME = 'signup.html'
    from magiclink import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.SIGNUP_TEMPLATE_NAME == settings.MAGICLINK_SIGNUP_TEMPLATE_NAME  # NOQA: E501


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


def test_email_ignore_case(settings):
    settings.MAGICLINK_EMAIL_IGNORE_CASE = True
    from magiclink import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.EMAIL_IGNORE_CASE == settings.MAGICLINK_EMAIL_IGNORE_CASE


def test_email_ignore_case_bad_value(settings):
    settings.MAGICLINK_EMAIL_IGNORE_CASE = 'Test'

    with pytest.raises(ImproperlyConfigured):
        from magiclink import settings
        reload(settings)


def test_require_signup(settings):
    settings.MAGICLINK_REQUIRE_SIGNUP = True
    from magiclink import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.REQUIRE_SIGNUP == settings.MAGICLINK_REQUIRE_SIGNUP


def test_require_signup_bad_value(settings):
    settings.MAGICLINK_REQUIRE_SIGNUP = 'Test'

    with pytest.raises(ImproperlyConfigured):
        from magiclink import settings
        reload(settings)


def test_email_as_username(settings):
    settings.MAGICLINK_EMAIL_AS_USERNAME = True
    from magiclink import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.EMAIL_AS_USERNAME == settings.MAGICLINK_EMAIL_AS_USERNAME


def test_email_as_username_bad_value(settings):
    settings.MAGICLINK_EMAIL_AS_USERNAME = 'Test'

    with pytest.raises(ImproperlyConfigured):
        from magiclink import settings
        reload(settings)


def test_allow_superuser_login(settings):
    settings.MAGICLINK_ALLOW_SUPERUSER_LOGIN = True
    from magiclink import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.ALLOW_SUPERUSER_LOGIN == settings.MAGICLINK_ALLOW_SUPERUSER_LOGIN  # NOQA: E501


def test_allow_superuser_login_bad_value(settings):
    settings.MAGICLINK_ALLOW_SUPERUSER_LOGIN = 'Test'

    with pytest.raises(ImproperlyConfigured):
        from magiclink import settings
        reload(settings)


def test_allow_staff_login(settings):
    settings.MAGICLINK_ALLOW_STAFF_LOGIN = True
    from magiclink import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.ALLOW_STAFF_LOGIN == settings.MAGICLINK_ALLOW_STAFF_LOGIN


def test_allow_staff_login_bad_value(settings):
    settings.MAGICLINK_ALLOW_STAFF_LOGIN = 'Test'

    with pytest.raises(ImproperlyConfigured):
        from magiclink import settings
        reload(settings)


def test_verify_include_email(settings):
    settings.MAGICLINK_VERIFY_INCLUDE_EMAIL = True
    from magiclink import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.VERIFY_INCLUDE_EMAIL == settings.MAGICLINK_VERIFY_INCLUDE_EMAIL  # NOQA: E501


def test_verify_include_email_bad_value(settings):
    settings.MAGICLINK_VERIFY_INCLUDE_EMAIL = 'Test'

    with pytest.raises(ImproperlyConfigured):
        from magiclink import settings
        reload(settings)


def test_require_same_browser(settings):
    settings.MAGICLINK_REQUIRE_SAME_BROWSER = True
    from magiclink import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.REQUIRE_SAME_BROWSER == settings.MAGICLINK_REQUIRE_SAME_BROWSER  # NOQA: E501


def test_require_same_browser_bad_value(settings):
    settings.MAGICLINK_REQUIRE_SAME_BROWSER = 'Test'

    with pytest.raises(ImproperlyConfigured):
        from magiclink import settings
        reload(settings)


def test_require_same_ip(settings):
    settings.MAGICLINK_REQUIRE_SAME_IP = True
    from magiclink import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.REQUIRE_SAME_IP == settings.MAGICLINK_REQUIRE_SAME_IP


def test_require_same_ip_bad_value(settings):
    settings.MAGICLINK_REQUIRE_SAME_IP = 'Test'

    with pytest.raises(ImproperlyConfigured):
        from magiclink import settings
        reload(settings)


def test_one_token_per_user(settings):
    settings.MAGICLINK_ONE_TOKEN_PER_USER = True
    from magiclink import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.ONE_TOKEN_PER_USER == settings.MAGICLINK_ONE_TOKEN_PER_USER  # NOQA: E501


def test_one_token_per_user_bad_value(settings):
    settings.MAGICLINK_ONE_TOKEN_PER_USER = 'Test'

    with pytest.raises(ImproperlyConfigured):
        from magiclink import settings
        reload(settings)


def test_email_styles(settings):
    settings.MAGICLINK_EMAIL_STYLES = {
        'logo_url': '',
        'background_color': '#ffffff',
        'main_text_color': '#000000',
        'button_background_color': '#0078be',
        'button_text_color': '#ffffff',
    }
    from magiclink import settings as mlsettings
    reload(mlsettings)
    assert mlsettings.EMAIL_STYLES == settings.MAGICLINK_EMAIL_STYLES


def test_email_styles_bad_value(settings):
    settings.MAGICLINK_EMAIL_STYLES = 'Test'

    with pytest.raises(ImproperlyConfigured):
        from magiclink import settings
        reload(settings)
