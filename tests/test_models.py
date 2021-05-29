from __future__ import annotations

from urllib.parse import quote

import pytest
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.urls import reverse

from magiclink.models import MagicLink

from .fixtures import magic_link, user  # NOQA: F401

User = get_user_model()


@pytest.mark.django_db
def test_model_string(magic_link):  # NOQA: F811
    request = HttpRequest()
    ml = magic_link(request)
    assert str(ml) == f'{ml.email} - {ml.expiry}'


@pytest.mark.django_db
def test_generate_url(magic_link):  # NOQA: F811
    request = HttpRequest()
    host = '127.0.0.1'
    login_url = reverse('magiclink:login_verify')
    request.META['SERVER_NAME'] = host
    request.META['SERVER_PORT'] = 80
    ml = magic_link(request)
    url = f'http://{host}{login_url}?token={ml.token}&email={quote(ml.email)}'
    assert MagicLink.generate_url(token=ml.token, email=ml.email, request=request) == url


@pytest.mark.django_db
def test_send_email(mocker, settings, magic_link):  # NOQA: F811
    from magiclink import settings as mlsettings
    send_mail = mocker.patch('magiclink.models.send_mail')
    render_to_string = mocker.patch('magiclink.models.render_to_string')

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
    MagicLink.send(ml, request, style=style)

    usr = User.objects.get(email=ml.email)
    context = {
        'subject': mlsettings.EMAIL_SUBJECT,
        'user': usr,
        'magiclink': MagicLink.generate_url(token=ml.token, email=ml.email, request=request),
        'expiry': ml.expiry,
        'ip_address': ml.ip_address,
        'created': ml.created,
        'style': style,
    }
    render_to_string.assert_has_calls([
        mocker.call(mlsettings.EMAIL_TEMPLATE_NAME_TEXT, context),
        mocker.call(mlsettings.EMAIL_TEMPLATE_NAME_HTML, context),
    ])
    send_mail.assert_called_once_with(
        subject=mlsettings.EMAIL_SUBJECT,
        message=mocker.ANY,
        recipient_list=[ml.email],
        from_email=settings.DEFAULT_FROM_EMAIL,
        html_message=mocker.ANY,
    )
