from __future__ import annotations

import logging

from django.contrib.auth import get_user_model
from django.http import HttpRequest

from .models import MagicLink, MagicLinkError
from .services import disable_magiclink, validate_magiclink

User = get_user_model()
log = logging.getLogger(__name__)


class MagicLinkBackend:
    @staticmethod
    def authenticate(request: HttpRequest, token: str = '', email: str = ''):
        log.debug(f'MagicLink authenticate token: {token} - email: {email}')

        if not token:
            log.warning('Token missing from authentication')
            return

        if not email:
            log.warning('Email address not supplied with token')
            return

        try:
            magiclink = MagicLink.objects.get(token=token)
        except MagicLink.DoesNotExist:
            log.warning(f'MagicLink with token "{token}" not found')
            return

        if magiclink.disabled:
            log.warning(f'MagicLink "{magiclink.pk}" is disabled')
            return

        try:
            user = validate_magiclink(ml=magiclink, email=email)
        except MagicLinkError as error:
            log.warning(error)
            return

        disable_magiclink(pk=magiclink.pk)
        log.info(f'{user} authenticated via MagicLink')
        return user

    @staticmethod
    def get_user(user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return
