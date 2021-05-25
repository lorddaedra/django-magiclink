from importlib import reload
from urllib.parse import urlencode

import pytest
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.urls import reverse

from .fixtures import magic_link, user  # NOQA: F401

User = get_user_model()


@pytest.mark.django_db
def test_login_verify(client, settings, user, magic_link):  # NOQA: F811
    url = reverse('magiclink:login_verify')
    request = HttpRequest()
    ml = magic_link(request)
    ml.ip_address = '127.0.0.1'  # This is a little hacky
    ml.save()

    params = {'token': ml.token}
    params['email'] = ml.email
    query = urlencode(params)
    url = f'{url}?{query}'

    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse(settings.LOGIN_REDIRECT_URL)

    needs_login_url = reverse('needs_login')
    needs_login_response = client.get(needs_login_url)
    assert needs_login_response.status_code == 200


@pytest.mark.django_db
def test_login_verify_with_redirect(client, settings, user, magic_link):  # NOQA: F811,E501
    url = reverse('magiclink:login_verify')
    request = HttpRequest()
    request.META['SERVER_NAME'] = '127.0.0.1'
    request.META['SERVER_PORT'] = 80
    ml = magic_link(request)
    ml.ip_address = '127.0.0.1'  # This is a little hacky
    redirect_url = reverse('no_login')
    ml.redirect_url = redirect_url
    ml.save()
    url = ml.generate_url(request)

    response = client.get(url)
    assert response.status_code == 302
    assert response.url == redirect_url


@pytest.mark.django_db
def test_login_verify_no_token_404(client, settings):
    settings.MAGICLINK_LOGIN_FAILED_TEMPLATE_NAME = ''
    from magiclink import settings as mlsettings
    reload(mlsettings)

    url = reverse('magiclink:login_verify')
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_login_verify_failed(client, settings):
    settings.MAGICLINK_LOGIN_FAILED_TEMPLATE_NAME = 'magiclink/login_failed.html'  # NOQA: E501
    from magiclink import settings as mlsettings
    reload(mlsettings)

    url = reverse('magiclink:login_verify')
    response = client.get(url)
    assert response.status_code == 200
    context = response.context_data
    assert context['login_error'] == 'A magic link with that token could not be found'  # NOQA: E501
    assert context['ONE_TOKEN_PER_USER'] == mlsettings.ONE_TOKEN_PER_USER
    assert context['ALLOW_SUPERUSER_LOGIN'] == mlsettings.ALLOW_SUPERUSER_LOGIN
    assert context['ALLOW_STAFF_LOGIN'] == mlsettings.ALLOW_STAFF_LOGIN
