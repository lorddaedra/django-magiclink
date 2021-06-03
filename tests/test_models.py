from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.http import HttpRequest

from magiclinks.models import MagicLink

from .fixtures import magic_link, user  # NOQA: F401

User = get_user_model()


@pytest.mark.django_db
def test_model_string(magic_link):  # NOQA: F811
    request = HttpRequest()
    magic_link(request)
    ml = MagicLink.objects.first()
    assert str(ml).endswith(' - test@example.com') is True
