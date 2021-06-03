from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.urls import reverse

from magiclinks.services import create_magiclink

from .fixtures import magic_link, user  # NOQA: F401

User = get_user_model()


@pytest.mark.django_db
def test_login_verify(client, settings, user, magic_link):  # NOQA: F811
    reverse('magiclinks:login_verify')
    request = HttpRequest()
    url = magic_link(request)

    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse(settings.LOGIN_REDIRECT_URL)

    needs_login_url = reverse('needs_login')
    needs_login_response = client.get(needs_login_url)
    assert needs_login_response.status_code == 200


@pytest.mark.django_db
def test_login_verify_with_redirect(client, settings, user):  # NOQA: F811,E501
    reverse('magiclinks:login_verify')
    next_url = reverse('no_login')
    url = create_magiclink(email=user.email, domain='127.0.0.1:8000', url_name='magiclinks:login_verify', next_url=next_url, limit_seconds=3)

    response = client.get(url)
    assert response.status_code == 302
    assert response.url == next_url


@pytest.mark.django_db
def test_login_verify_failed(client, settings, magic_link):  # NOQA: F811
    request = HttpRequest()
    url: str = magic_link(request) + '1234'

    response = client.get(url, follow=True)
    messages = list(response.context['messages'])
    assert len(messages) == 1
    assert str(messages[0]) == 'Token is invalid or expired. Please, try again.'  # NOQA: E501
