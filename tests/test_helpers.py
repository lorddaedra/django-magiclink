from datetime import timedelta
from importlib import reload

import pytest
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.urls import reverse
from django.utils import timezone

from magiclink import settings as mlsettings
from magiclink.helpers import create_magiclink, get_or_create_user
from magiclink.models import MagicLink, MagicLinkError

from .fixtures import user  # NOQA: F401
from .models import CustomUserEmailOnly, CustomUserFullName, CustomUserName

User = get_user_model()


@pytest.mark.django_db
def test_create_magiclink(settings, freezer):
    freezer.move_to('2000-01-01T00:00:00')

    email = 'test@example.com'
    remote_addr = '127.0.0.1'
    expiry = timezone.now() + timedelta(seconds=mlsettings.AUTH_TIMEOUT)
    request = HttpRequest()
    request.META['REMOTE_ADDR'] = remote_addr
    magic_link = create_magiclink(email, request)
    assert magic_link.email == email
    assert len(magic_link.token) == mlsettings.TOKEN_LENGTH
    assert magic_link.expiry == expiry
    assert magic_link.redirect_url == reverse(settings.LOGIN_REDIRECT_URL)
    assert magic_link.ip_address == remote_addr


@pytest.mark.django_db
def test_create_magiclink_redirect_url(settings):
    email = 'test@example.com'
    request = HttpRequest()
    redirect_url = '/test/'
    magic_link = create_magiclink(email, request, redirect_url=redirect_url)
    assert magic_link.email == email
    assert magic_link.redirect_url == redirect_url


@pytest.mark.django_db
def test_create_magiclink_email_ignore_case(settings):
    email = 'TEST@example.com'
    request = HttpRequest()
    magic_link = create_magiclink(email, request)
    assert magic_link.email == email.lower()


@pytest.mark.django_db
def test_create_magiclink_email_ignore_case_off(settings):
    settings.MAGICLINK_EMAIL_IGNORE_CASE = False
    from magiclink import settings
    reload(settings)

    email = 'TEST@example.com'
    request = HttpRequest()
    magic_link = create_magiclink(email, request)
    assert magic_link.email == email


@pytest.mark.django_db
def test_create_magiclink_one_token_per_user(settings, freezer):
    email = 'test@example.com'
    request = HttpRequest()
    freezer.move_to('2000-01-01T00:00:00')
    magic_link = create_magiclink(email, request)
    assert magic_link.disabled is False

    freezer.move_to('2000-01-01T00:00:31')
    create_magiclink(email, request)

    magic_link = MagicLink.objects.get(token=magic_link.token)
    assert magic_link.disabled is True
    assert magic_link.email == email


@pytest.mark.django_db
def test_create_magiclink_login_request_time_limit(settings):
    email = 'test@example.com'
    request = HttpRequest()
    create_magiclink(email, request)
    with pytest.raises(MagicLinkError):
        create_magiclink(email, request)


@pytest.mark.django_db
def test_get_or_create_user_exists(user):  # NOQA: F811
    usr = get_or_create_user(email=user.email)
    assert usr == user
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_get_or_create_user_exists_ignore_case(settings, user):  # NOQA: F811
    settings.MAGICLINK_EMAIL_IGNORE_CASE = True
    from magiclink import settings
    reload(settings)

    usr = get_or_create_user(email=user.email.upper())
    assert usr == user
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_get_or_create_user_email_as_username(settings):
    email = 'test@example.com'
    usr = get_or_create_user(email=email)
    assert usr.email == email
    assert usr.username == email


@pytest.mark.django_db
def test_get_or_create_user_random_username(settings):
    settings.MAGICLINK_EMAIL_AS_USERNAME = False
    from magiclink import settings
    reload(settings)

    email = 'test@example.com'
    usr = get_or_create_user(email=email)
    assert usr.email == email
    assert usr.username != email
    assert len(usr.username) == 10


@pytest.mark.django_db
def test_get_or_create_user_first_name(settings):
    first_name = 'fname'
    usr = get_or_create_user(email='test@example.com', first_name=first_name)
    assert usr.first_name == first_name


@pytest.mark.django_db
def test_get_or_create_user_last_name(settings):
    last_name = 'lname'
    usr = get_or_create_user(email='test@example.com', last_name=last_name)
    assert usr.last_name == last_name


@pytest.mark.django_db
def test_get_or_create_user_no_username(mocker, settings):
    gum = mocker.patch('magiclink.helpers.get_user_model')
    gum.return_value = CustomUserEmailOnly

    from magiclink.helpers import get_or_create_user
    email = 'test@example.com'
    usr = get_or_create_user(email=email)
    assert usr.email == email


@pytest.mark.django_db
def test_get_or_create_user_full_name(mocker, settings):
    gum = mocker.patch('magiclink.helpers.get_user_model')
    gum.return_value = CustomUserFullName

    from magiclink.helpers import get_or_create_user
    email = 'test@example.com'
    first = 'fname'
    last = 'lname'
    usr = get_or_create_user(email=email, first_name=first, last_name=last)
    assert usr.email == email
    assert usr.full_name == f'{first} {last}'


@pytest.mark.django_db
def test_get_or_create_user_name(mocker, settings):
    gum = mocker.patch('magiclink.helpers.get_user_model')
    gum.return_value = CustomUserName

    from magiclink.helpers import get_or_create_user
    email = 'test@example.com'
    first = 'fname'
    last = 'lname'
    usr = get_or_create_user(email=email, first_name=first, last_name=last)
    assert usr.email == email
    assert usr.name == f'{first} {last}'
