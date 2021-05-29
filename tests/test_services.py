from __future__ import annotations

from datetime import timedelta
from urllib.parse import quote

import pytest
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest
from django.urls import reverse
from django.utils import timezone

from magiclink import settings as mlsettings
from magiclink.models import MagicLink, MagicLinkError
from magiclink.services import create_magiclink, create_user, generate_url, send_magiclink, validate_magiclink
from magiclink.utils import get_client_ip

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
    magic_link = create_magiclink(email=email, ip_address=get_client_ip(request))  # NOQA: F811
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
    magic_link = create_magiclink(email=email, ip_address=get_client_ip(request), redirect_url=redirect_url)  # NOQA: F811
    assert magic_link.email == email
    assert magic_link.redirect_url == redirect_url


@pytest.mark.django_db
def test_create_magiclink_email_ignore_case(settings):
    email = 'TEST@example.com'
    request = HttpRequest()
    magic_link = create_magiclink(email=email, ip_address=get_client_ip(request))  # NOQA: F811
    assert magic_link.email == email.lower()


@pytest.mark.django_db
def test_create_magiclink_one_token_per_user(settings, freezer):
    email = 'test@example.com'
    request = HttpRequest()
    freezer.move_to('2000-01-01T00:00:00')
    magic_link = create_magiclink(email=email, ip_address=get_client_ip(request))  # NOQA: F811
    assert magic_link.disabled is False

    freezer.move_to('2000-01-01T00:00:31')
    create_magiclink(email=email, ip_address=get_client_ip(request))

    magic_link = MagicLink.objects.get(token=magic_link.token)  # NOQA: F811
    assert magic_link.disabled is True
    assert magic_link.email == email


@pytest.mark.django_db
def test_create_magiclink_login_request_time_limit(settings):
    email = 'test@example.com'
    request = HttpRequest()
    create_magiclink(email=email, ip_address=get_client_ip(request))
    with pytest.raises(MagicLinkError):
        create_magiclink(email=email, ip_address=get_client_ip(request))


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
    ml_user = validate_magiclink(ml=ml, email=user.email)
    assert ml_user == user


@pytest.mark.django_db
def test_validate_email_ignore_case(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    ml = magic_link(request)
    ml_user = validate_magiclink(ml=ml, email=user.email.upper())
    assert ml_user == user


@pytest.mark.django_db
def test_validate_wrong_email(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    ml = magic_link(request)
    email = 'fake@email.com'
    with pytest.raises(MagicLinkError) as error:
        validate_magiclink(ml=ml, email=email)

    error.match('Email address does not match')


@pytest.mark.django_db
def test_validate_expired(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    ml = magic_link(request)
    ml.expiry = timezone.now() - timedelta(seconds=1)
    ml.save()

    with pytest.raises(MagicLinkError) as error:
        validate_magiclink(ml=ml, email=user.email)

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
        validate_magiclink(ml=ml, email=user.email)

    error.match('Magic link has been used')


@pytest.mark.django_db
def test_send_email(mocker, settings, magic_link):  # NOQA: F811
    send_mail = mocker.patch('magiclink.services.send_mail')
    render_to_string = mocker.patch('magiclink.services.render_to_string')

    request = HttpRequest()
    request.META['SERVER_NAME'] = '127.0.0.1'
    request.META['SERVER_PORT'] = 80

    ml = magic_link(request)
    style: dict[str, str] = {
        'logo_url': '',
        'background_color': '#ffffff',
        'main_text_color': '#000000',
        'button_background_color': '#0078be',
        'button_text_color': '#ffffff',
    }
    send_magiclink(ml=ml, domain=get_current_site(request).domain, subject='Your login magic link', style=style)

    usr = User.objects.get(email=ml.email)
    context = {
        'subject': 'Your login magic link',
        'user': usr,
        'magiclink': generate_url(token=ml.token, email=ml.email, domain=get_current_site(request).domain),
        'expiry': ml.expiry,
        'ip_address': ml.ip_address,
        'created': ml.created,
        'style': style,
    }
    render_to_string.assert_has_calls([
        mocker.call('magiclink/login_email.txt', context),
        mocker.call('magiclink/login_email.html', context),
    ])
    send_mail.assert_called_once_with(
        subject='Your login magic link',
        message=mocker.ANY,
        recipient_list=[ml.email],
        from_email=settings.DEFAULT_FROM_EMAIL,
        html_message=mocker.ANY,
    )


@pytest.mark.django_db
def test_generate_url(magic_link):  # NOQA: F811
    request = HttpRequest()
    host = '127.0.0.1'
    login_url = reverse('magiclink:login_verify')
    request.META['SERVER_NAME'] = host
    request.META['SERVER_PORT'] = 80
    ml = magic_link(request)
    url = f'https://{host}{login_url}?token={ml.token}&email={quote(ml.email)}'
    assert generate_url(token=ml.token, email=ml.email, domain=get_current_site(request).domain) == url
