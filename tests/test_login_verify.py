from __future__ import annotations

from importlib import reload
from urllib.parse import urlencode

import pytest
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core import signing
from django.http import HttpRequest
from django.urls import reverse

from magiclink.services import generate_url
from magiclink.settings import REGISTRATION_SALT

from .fixtures import magic_link, user  # NOQA: F401

User = get_user_model()


@pytest.mark.django_db
def test_login_verify(client, settings, user, magic_link):  # NOQA: F811
    url = reverse('magiclink:login_verify')
    request = HttpRequest()
    ml = magic_link(request)
    ml.ip_address = '127.0.0.1'  # This is a little hacky
    ml.save()

    signed_token: str = signing.dumps(obj={'token': ml.token, 'email': ml.email}, salt=REGISTRATION_SALT)
    params = {'token': signed_token}
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
    url = generate_url(token=ml.token, email=ml.email, domain=get_current_site(request).domain)

    response = client.get(url)
    assert response.status_code == 302
    assert response.url == redirect_url


@pytest.mark.django_db
def test_login_verify_failed(client, settings):
    from magiclink import settings as mlsettings
    reload(mlsettings)

    url = reverse('magiclink:login_verify')

    signed_token: str = signing.dumps(obj={'token': '', 'email': ''}, salt=REGISTRATION_SALT)
    params = {'token': signed_token}
    query = urlencode(params)
    url = f'{url}?{query}'

    response = client.get(url)
    assert response.status_code == 200
    context = response.context_data
    assert context['login_error'] == 'A magic link with that token could not be found'  # NOQA: E501
