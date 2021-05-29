from __future__ import annotations

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.urls import reverse
from django.utils import timezone

from magiclink import settings as mlsettings
from magiclink.models import MagicLink, MagicLinkError
from magiclink.services import create_magiclink, create_user, validate

from .fixtures import magic_link, user  # NOQA: F401

User = get_user_model()


@pytest.mark.django_db
def test_create_magiclink(settings, freezer):
    freezer.move_to('2000-01-01T00:00:00')

    email = 'test@example.com'
    remote_addr = '127.0.0.1'
    expiry = timezone.now() + timedelta(seconds=mlsettings.AUTH_TIMEOUT)
    request = HttpRequest()
    request.META['REMOTE_ADDR'] = remote_addr
    magic_link = create_magiclink(email=email, request=request)  # NOQA: F811
    assert magic_link.email == email
    assert len(magic_link.token) >= 43
    assert magic_link.expiry == expiry
    assert magic_link.redirect_url == reverse(settings.LOGIN_REDIRECT_URL)
    assert magic_link.ip_address == remote_addr


@pytest.mark.django_db
def test_create_magiclink_redirect_url(settings):
    email = 'test@example.com'
    request = HttpRequest()
    redirect_url = '/test/'
    magic_link = create_magiclink(email=email, request=request, redirect_url=redirect_url)  # NOQA: F811
    assert magic_link.email == email
    assert magic_link.redirect_url == redirect_url


@pytest.mark.django_db
def test_create_magiclink_email_ignore_case(settings):
    email = 'TEST@example.com'
    request = HttpRequest()
    magic_link = create_magiclink(email=email, request=request)  # NOQA: F811
    assert magic_link.email == email.lower()


@pytest.mark.django_db
def test_create_magiclink_one_token_per_user(settings, freezer):
    email = 'test@example.com'
    request = HttpRequest()
    freezer.move_to('2000-01-01T00:00:00')
    magic_link = create_magiclink(email=email, request=request)  # NOQA: F811
    assert magic_link.disabled is False

    freezer.move_to('2000-01-01T00:00:31')
    create_magiclink(email=email, request=request)

    magic_link = MagicLink.objects.get(token=magic_link.token)  # NOQA: F811
    assert magic_link.disabled is True
    assert magic_link.email == email


@pytest.mark.django_db
def test_create_magiclink_login_request_time_limit(settings):
    email = 'test@example.com'
    request = HttpRequest()
    create_magiclink(email=email, request=request)
    with pytest.raises(MagicLinkError):
        create_magiclink(email=email, request=request)


@pytest.mark.django_db
def test_create_user_random_username(settings):
    email = 'test@example.com'
    create_user(email=email)
    usr = User.objects.latest()
    assert usr.email == email
    assert usr.username != email
    assert len(usr.username) == 32


@pytest.mark.django_db
def test_create_user_no_username(settings):
    email = 'test@example.com'
    create_user(email=email)
    assert User.objects.latest().email == email


@pytest.mark.django_db
def test_validate(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    ml = magic_link(request)
    ml_user = validate(ml=ml, email=user.email)
    assert ml_user == user


@pytest.mark.django_db
def test_validate_email_ignore_case(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    ml = magic_link(request)
    ml_user = validate(ml=ml, email=user.email.upper())
    assert ml_user == user


@pytest.mark.django_db
def test_validate_wrong_email(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    ml = magic_link(request)
    email = 'fake@email.com'
    with pytest.raises(MagicLinkError) as error:
        validate(ml=ml, email=email)

    error.match('Email address does not match')


@pytest.mark.django_db
def test_validate_expired(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    ml = magic_link(request)
    ml.expiry = timezone.now() - timedelta(seconds=1)
    ml.save()

    with pytest.raises(MagicLinkError) as error:
        validate(ml=ml, email=user.email)

    error.match('Magic link has expired')

    ml = MagicLink.objects.get(token=ml.token)
    assert ml.disabled is True


@pytest.mark.django_db
def test_validate_used(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    ml = magic_link(request)
    ml.disabled = True
    ml.save()
    with pytest.raises(MagicLinkError) as error:
        validate(ml=ml, email=user.email)

    error.match('Magic link has been used')
