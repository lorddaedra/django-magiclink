from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model

from magiclink.services import create_magiclink, create_user
from magiclink.utils import get_client_ip

User = get_user_model()


@pytest.fixture()
def user():
    create_user(email='test@example.com')
    return User.objects.latest()


@pytest.fixture()
def magic_link(user):

    def _create(request):
        return create_magiclink(email=user.email, ip_address=get_client_ip(request), redirect_url='')

    return _create
