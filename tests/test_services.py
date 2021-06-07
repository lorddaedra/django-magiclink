from __future__ import annotations

from urllib.parse import unquote_plus

import pytest
from django.contrib.auth import get_user_model
from django.core import signing
from django.http import HttpRequest
from django.urls import reverse

from magiclinks.exceptions import MagicLinkError
from magiclinks.models import MagicLink
from magiclinks.services import create_magiclink, send_magiclink
from magiclinks.settings import REGISTRATION_SALT

from .fixtures import magic_link, user  # NOQA: F401

User = get_user_model()


@pytest.mark.django_db
def test_create_magiclink(settings, freezer):
    freezer.move_to('2000-01-01T00:00:00')
    email = 'Test@example.com'
    domain = '127.0.0.1:8000'
    url_name = 'magiclinks:login_verify'
    magic_link = create_magiclink(email=email, domain=domain, url_name=url_name, next_url='', limit_seconds=12)  # NOQA: F811
    assert domain in magic_link
    assert reverse(url_name) in magic_link
    token = unquote_plus(magic_link.split('=')[1])
    assert len(token.split(':')[-1]) >= 43
    data = signing.loads(token, salt=REGISTRATION_SALT, max_age=900)
    assert data['email'] == email.lower()
    assert data['next'] == reverse(settings.LOGIN_REDIRECT_URL)
    assert MagicLink.objects.get(pk=data['pk']).email == email.lower()
    with pytest.raises(MagicLinkError):
        create_magiclink(email=email, domain=domain, url_name=url_name, next_url='', limit_seconds=12)  # NOQA: F811


@pytest.mark.django_db
def test_create_magiclink_next_url(settings):
    email = 'test@example.com'
    domain = '127.0.0.1:8000'
    url_name = 'magiclinks:login_verify'
    next = '/test/'
    magic_link = create_magiclink(email=email, domain=domain, url_name=url_name, next_url=next, limit_seconds=3)  # NOQA: F811
    token = unquote_plus(magic_link.split('=')[1])
    data = signing.loads(token, salt=REGISTRATION_SALT)
    assert data['next'] == next


@pytest.mark.django_db
def test_send_email(mocker, settings, user, magic_link):  # NOQA: F811
    send_mail = mocker.patch('magiclinks.services.send_mail')
    # render_to_string = mocker.patch('magiclinks.services.render_to_string')

    request = HttpRequest()
    request.META['SERVER_NAME'] = '127.0.0.1'
    request.META['SERVER_PORT'] = 80
    magiclink = magic_link(request)

    style: dict[str, str] = {
        'logo_url': '',
        'background_color': '#ffffff',
        'main_text_color': '#000000',
        'button_background_color': '#0078be',
        'button_text_color': '#ffffff',
    }
    send_magiclink(email=user.email, magiclink=magiclink, subject='Your login magic link', style=style)

    # context = {
    #     'subject': 'Your login magic link',
    #     'user': user,
    #     'magiclink': magiclink,
    #     'style': style,
    # }
    # render_to_string.assert_has_calls([
    #     mocker.call('magiclinks/login_email.txt', context),
    #     mocker.call('magiclinks/login_email.html', context),
    # ])
    send_mail.assert_called_once_with(
        subject='Your login magic link',
        message=mocker.ANY,
        recipient_list=[user.email],
        from_email=settings.DEFAULT_FROM_EMAIL,
        html_message=mocker.ANY,
    )
