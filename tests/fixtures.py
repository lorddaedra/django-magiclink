from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model

from magiclinks.services import create_magiclink

User = get_user_model()


@pytest.fixture()
def user():
    return User.objects.create_user(username='testuser', email='test@example.com')


@pytest.fixture()
def magic_link(user):

    def _create(request):
        return create_magiclink(email=user.email, domain='127.0.0.1:8000', url_name='magiclinks:login_verify', next_url='', limit_seconds=3)

    return _create
