from __future__ import annotations

from urllib.parse import unquote_plus

import pytest
from django.contrib.auth import get_user_model
from django.core import signing
from django.http import HttpRequest

from magiclinks.backends import MagicLinksBackend
from magiclinks.models import MagicLink
from magiclinks.settings import REGISTRATION_SALT

from .fixtures import magic_link, user  # NOQA: F401

User = get_user_model()


@pytest.mark.django_db
def test_auth_backend(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    token = unquote_plus(magic_link(request).split('=')[1])
    user = MagicLinksBackend().authenticate(request=request, token=token)
    assert user
    ml = MagicLink.objects.filter(pk=signing.loads(token, salt=REGISTRATION_SALT)['pk']).first()
    assert ml is None


@pytest.mark.django_db
def test_auth_backend_no_token(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    user = MagicLinksBackend().authenticate(request=request, token='')
    assert user is None


@pytest.mark.django_db
def test_auth_backend_fake_token(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    user = MagicLinksBackend().authenticate(request=request, token='fake')
    assert user is None


@pytest.mark.django_db
def test_auth_backend_expired_token(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    token = unquote_plus(magic_link(request).split('=')[1])
    user = MagicLinksBackend().authenticate(request=request, token=token, expiry_seconds=0)
    assert user is None


@pytest.mark.django_db
def test_auth_backend_no_database_record(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    token = unquote_plus(magic_link(request).split('=')[1])
    MagicLink.objects.all().delete()
    user = MagicLinksBackend().authenticate(request=request, token=token)
    assert user is None


@pytest.mark.django_db
def test_auth_backend_invalid(user, magic_link):  # NOQA: F811
    request = HttpRequest()
    token = unquote_plus(magic_link(request).split('=')[1])
    User.objects.all().delete()
    user = MagicLinksBackend().authenticate(request=request, token=token)
    assert user is None
