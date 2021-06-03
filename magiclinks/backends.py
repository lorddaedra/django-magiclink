from __future__ import annotations

import logging
from typing import Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core import signing
from django.http import HttpRequest

from .models import MagicLink
from .services import delete_magiclink
from .settings import REGISTRATION_SALT

User = get_user_model()
log = logging.getLogger(__name__)


class MagicLinksBackend(ModelBackend):
    def authenticate(self, request: Optional[HttpRequest], username: Optional[str] = None, password: Optional[str] = None, token: str = '',
                     expiry_seconds: int = 900, **kwargs):
        if not token:
            return

        try:
            token_data: dict[str, str] = signing.loads(token, salt=REGISTRATION_SALT, max_age=expiry_seconds)
        except signing.SignatureExpired:
            return
        except signing.BadSignature:
            return
        else:
            pk: str = token_data['pk']
            email: str = token_data['email']

        if not MagicLink.objects.filter(pk=pk).exists():
            return

        delete_magiclink(pk=pk)

        try:
            user = User._default_manager.get(email=email)
        except User.DoesNotExist:
            return

        return user if self.user_can_authenticate(user) else None
