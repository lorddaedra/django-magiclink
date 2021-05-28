from datetime import timedelta
from urllib.parse import quote

import pytest
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.urls import reverse
from django.utils import timezone

from magiclink import settings
from magiclink.models import MagicLink, MagicLinkError

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
    assert ml.generate_url(request) == url


@pytest.mark.django_db
def test_send_email(mocker, settings, magic_link):  # NOQA: F811
    from magiclink import settings as mlsettings
    send_mail = mocker.patch('magiclink.models.send_mail')
    render_to_string = mocker.patch('magiclink.models.render_to_string')

    request = HttpRequest()
    request.META['SERVER_NAME'] = '127.0.0.1'
    request.META['SERVER_PORT'] = 80

    ml = magic_link(request)
    ml.send(request)

    usr = User.objects.get(email=ml.email)
    context = {
        'subject': mlsettings.EMAIL_SUBJECT,
        'user': usr,
        'magiclink': ml.generate_url(request),
        'expiry': ml.expiry,
        'ip_address': ml.ip_address,
        'created': ml.created,
        'token_uses': mlsettings.TOKEN_USES,
        'style': mlsettings.EMAIL_STYLES,
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


@pytest.mark.django_db
def test_validate(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    ml = magic_link(request)
    ml_user = MagicLink.validate(ml, email=user.email)
    assert ml_user == user


@pytest.mark.django_db
def test_validate_email_ignore_case(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    ml = magic_link(request)
    ml_user = MagicLink.validate(ml, email=user.email.upper())
    assert ml_user == user


@pytest.mark.django_db
def test_validate_wrong_email(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    ml = magic_link(request)
    email = 'fake@email.com'
    with pytest.raises(MagicLinkError) as error:
        MagicLink.validate(ml, email=email)

    error.match('Email address does not match')


@pytest.mark.django_db
def test_validate_expired(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    ml = magic_link(request)
    ml.expiry = timezone.now() - timedelta(seconds=1)
    ml.save()

    with pytest.raises(MagicLinkError) as error:
        MagicLink.validate(ml, email=user.email)

    error.match('Magic link has expired')

    ml = MagicLink.objects.get(token=ml.token)
    assert ml.times_used == 1
    assert ml.disabled is True


@pytest.mark.django_db
def test_validate_used_times(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    ml = magic_link(request)
    ml.times_used = settings.TOKEN_USES
    ml.save()
    with pytest.raises(MagicLinkError) as error:
        MagicLink.validate(ml, email=user.email)

    error.match('Magic link has been used too many times')

    ml = MagicLink.objects.get(token=ml.token)
    assert ml.times_used == settings.TOKEN_USES + 1
    assert ml.disabled is True
