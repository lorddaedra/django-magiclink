from __future__ import annotations

import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.http import HttpRequest
from django.utils import timezone
from django.utils.crypto import get_random_string

from magiclink.models import MagicLink, MagicLinkError
from magiclink.settings import AUTH_TIMEOUT, LOGIN_REQUEST_TIME_LIMIT, TOKEN_LENGTH
from magiclink.utils import get_client_ip, get_url_path

logger = logging.getLogger(__name__)
User = get_user_model()


def create_user(*, email: str) -> None:
    """Create `user`."""
    logger.info('Creating user')
    email = email.lower()
    password: str = make_password(None)
    user = User(email=email, password=password, is_staff=False, is_superuser=False)
    user.username = str(user.pk).replace('-', '')
    user.save()


def create_magiclink(*, email: str, request: HttpRequest, redirect_url: str = '') -> MagicLink:
    email = email.lower()

    limit = timezone.now() - timedelta(seconds=LOGIN_REQUEST_TIME_LIMIT)  # NOQA: E501
    over_limit = MagicLink.objects.filter(email=email, created__gte=limit)
    if over_limit:
        raise MagicLinkError('Too many magic login requests')

    MagicLink.objects.filter(email=email, disabled=False).update(disabled=True)

    if not redirect_url:
        redirect_url = get_url_path(settings.LOGIN_REDIRECT_URL)

    expiry = timezone.now() + timedelta(seconds=AUTH_TIMEOUT)
    magic_link = MagicLink.objects.create(email=email, token=get_random_string(length=TOKEN_LENGTH), expiry=expiry, redirect_url=redirect_url,
                                          ip_address=get_client_ip(request))
    return magic_link


def disable_magiclink(*, pk: int) -> None:
    MagicLink.objects.filter(pk=pk).update(disabled=True)


def validate(*, ml: 'MagicLink', email: str = '') -> AbstractUser:
    if email:
        email = email.lower()

    if ml.email != email:
        raise MagicLinkError('Email address does not match')

    if timezone.now() > ml.expiry:
        disable_magiclink(pk=ml.pk)
        raise MagicLinkError('Magic link has expired')

    if ml.disabled:
        raise MagicLinkError('Magic link has been used')

    user = User.objects.get(email=ml.email)

    return user
